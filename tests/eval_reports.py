from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any


def write_deepeval_report(
    *,
    app_name: str,
    dataset_path: str,
    cases: list[dict[str, Any]],
    output_dir: str | Path = "reports",
) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    path = directory / f"deepeval-{app_name}-report-{timestamp}.json"
    payload = {
        "app_name": app_name,
        "dataset_path": dataset_path,
        "run_timestamp": datetime.now(UTC).isoformat(),
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "metric_averages": _metric_averages(cases),
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def metric_result(metric: object) -> dict[str, object]:
    return {
        "name": getattr(metric, "name", metric.__class__.__name__),
        "score": getattr(metric, "score", None),
        "passed": getattr(metric, "success", None),
        "reason": getattr(metric, "reason", None),
    }


def assert_metrics_passed(report_cases: list[dict[str, Any]]) -> None:
    failures = []
    for case in report_cases:
        for metric in case["metrics"]:
            if not metric["passed"]:
                failures.append(
                    f"{case.get('id', case['input'])}: {metric['name']} failed "
                    f"with score={metric['score']}, reason={metric['reason']}"
                )
    assert not failures, "\n".join(failures)


def _metric_averages(cases: list[dict[str, Any]]) -> dict[str, float]:
    values: dict[str, list[float]] = {}
    for case in cases:
        for metric in case["metrics"]:
            score = metric.get("score")
            if score is not None:
                values.setdefault(str(metric["name"]), []).append(float(score))
    return {
        metric_name: sum(scores) / len(scores)
        for metric_name, scores in values.items()
        if scores
    }
