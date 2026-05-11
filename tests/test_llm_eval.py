from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams
from dotenv import load_dotenv

from eval_reports import assert_metrics_passed, metric_result, write_deepeval_report
from llm_qa_app.providers import OpenAIChatProvider
from llm_qa_app.qa_app import QAApp


load_dotenv()


def test_qa_app_answer_quality_with_deepeval():
    if os.getenv("RUN_LLM_EVAL") != "1":
        pytest.skip("Set RUN_LLM_EVAL=1 to run LLM quality evaluation.")
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required to run LLM quality evaluation.")

    model = os.getenv("DEEPEVAL_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    app = QAApp(provider=OpenAIChatProvider())
    report_cases = []

    for case in _load_cases(Path("data/eval_cases/qa_sample.jsonl")):
        actual_output = app.answer(case["input"])
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=actual_output,
            expected_output=case["expected_output"],
        )

        metrics = [
            AnswerRelevancyMetric(threshold=0.7, model=model, include_reason=True),
            GEval(
                name="Correctness",
                evaluation_steps=[
                    "Compare the actual output with the expected output.",
                    "Penalize factual contradictions.",
                    "Penalize missing details that are necessary to answer the input.",
                    "Accept wording differences when the meaning is equivalent.",
                ],
                evaluation_params=[
                    SingleTurnParams.INPUT,
                    SingleTurnParams.ACTUAL_OUTPUT,
                    SingleTurnParams.EXPECTED_OUTPUT,
                ],
                threshold=0.7,
                model=model,
            ),
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
                "actual_output": actual_output,
                "metrics": metric_results,
            }
        )

    write_deepeval_report(
        app_name="qa",
        dataset_path="data/eval_cases/qa_sample.jsonl",
        cases=report_cases,
    )
    assert_metrics_passed(report_cases)


def _load_cases(path: Path) -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            cases.append(json.loads(raw_line))
    return cases
