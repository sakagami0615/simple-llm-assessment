from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from deepeval.metrics import AnswerRelevancyMetric, ContextualRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv

from eval_reports import assert_metrics_passed, metric_result, write_deepeval_report
from rag_app.rag_app import LangChainRAGApp


load_dotenv()


def test_rag_app_answer_quality_with_deepeval():
    if os.getenv("RUN_LLM_EVAL") != "1":
        pytest.skip("Set RUN_LLM_EVAL=1 to run RAG quality evaluation.")
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required to run RAG quality evaluation.")

    model = os.getenv("DEEPEVAL_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    cases = _load_cases(Path("data/eval_cases/rag_sample.jsonl"))
    app = LangChainRAGApp.from_contexts(
        context
        for case in cases
        for context in case["retrieval_context"]
    )
    report_cases = []

    for case in cases:
        result = app.answer(case["input"])
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result.answer,
            expected_output=case["expected_output"],
            retrieval_context=result.retrieval_context,
        )

        metrics = [
            AnswerRelevancyMetric(threshold=0.7, model=model, include_reason=True),
            FaithfulnessMetric(threshold=0.7, model=model, include_reason=True),
            ContextualRelevancyMetric(threshold=0.7, model=model, include_reason=True),
        ]

        metric_results = []
        for metric in metrics:
            metric.measure(test_case)
            metric_results.append(metric_result(metric))

        report_cases.append(
            {
                "id": case.get("id"),
                "input": case["input"],
                "expected_output": case["expected_output"],
                "actual_output": result.answer,
                "retrieval_context": result.retrieval_context,
                "metrics": metric_results,
            }
        )

    write_deepeval_report(
        app_name="rag",
        dataset_path="data/eval_cases/rag_sample.jsonl",
        cases=report_cases,
    )
    assert_metrics_passed(report_cases)


def _load_cases(path: Path) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            cases.append(json.loads(raw_line))
    return cases
