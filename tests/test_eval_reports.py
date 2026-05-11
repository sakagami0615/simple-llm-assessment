from __future__ import annotations

import json

from eval_reports import write_deepeval_report


def test_write_deepeval_report_outputs_case_metrics_and_summary(tmp_path):
    report_path = write_deepeval_report(
        app_name="qa",
        dataset_path="data/eval_cases/qa_sample.jsonl",
        cases=[
            {
                "id": "qa_001",
                "input": "question",
                "expected_output": "expected",
                "actual_output": "actual",
                "metrics": [
                    {
                        "name": "AnswerRelevancyMetric",
                        "score": 0.8,
                        "passed": True,
                        "reason": "ok",
                    }
                ],
            }
        ],
        output_dir=tmp_path,
    )

    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert report_path.name.startswith("deepeval-qa-report-")
    assert payload["app_name"] == "qa"
    assert payload["dataset_path"] == "data/eval_cases/qa_sample.jsonl"
    assert payload["summary"] == {
        "case_count": 1,
        "metric_averages": {"AnswerRelevancyMetric": 0.8},
    }
    assert payload["cases"][0]["metrics"][0]["passed"] is True
