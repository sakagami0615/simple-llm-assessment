from pathlib import Path

import pytest

from local_llm_eval.config import ConfigError
from local_llm_eval.planner import EvaluationJob, plan_suite


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def create_suite_files(root: Path) -> Path:
    write(
        root / "config" / "models" / "ollama.yaml",
        """
id: ollama-llama3
provider: openai_compatible
base_url: http://localhost:11434/v1
model: llama3.1:8b
generation:
  temperature: 0
""",
    )
    write(
        root / "config" / "benchmarks" / "mmlu.yaml",
        """
id: mmlu
runner: lm-evaluation-harness
task: mmlu
runner_params:
  num_fewshot: 5
metrics:
  - acc
""",
    )
    return write(
        root / "config" / "suites" / "baseline.yaml",
        """
id: baseline
models:
  - models/ollama.yaml
benchmarks:
  - benchmarks/mmlu.yaml
""",
    )


def test_plan_suite_expands_model_by_benchmark_jobs(tmp_path: Path) -> None:
    suite_path = create_suite_files(tmp_path)

    plan = plan_suite(suite_path)

    assert plan.suite.id == "baseline"
    assert plan.jobs == [
        EvaluationJob(
            model=plan.models[0],
            benchmark=plan.benchmarks[0],
            output_name="ollama-llama3/mmlu",
        )
    ]


def test_plan_suite_rejects_missing_referenced_file(tmp_path: Path) -> None:
    suite_path = write(
        tmp_path / "config" / "suites" / "broken.yaml",
        """
id: broken
models:
  - models/missing.yaml
benchmarks:
  - benchmarks/mmlu.yaml
""",
    )

    with pytest.raises(ConfigError, match="Referenced file does not exist"):
        plan_suite(suite_path)


def test_plan_suite_rejects_missing_dataset_file(tmp_path: Path) -> None:
    write(
        tmp_path / "config" / "models" / "ollama.yaml",
        """
id: ollama-llama3
provider: openai_compatible
base_url: http://localhost:11434/v1
model: llama3.1:8b
generation: {}
""",
    )
    write(
        tmp_path / "config" / "benchmarks" / "qa.yaml",
        """
id: my_internal_qa
runner: OpenCompass
dataset: datasets/missing.json
dataset_format: chatml
evaluator: cascade
metrics:
  - exact_match
""",
    )
    suite_path = write(
        tmp_path / "config" / "suites" / "baseline.yaml",
        """
id: baseline
models:
  - models/ollama.yaml
benchmarks:
  - benchmarks/qa.yaml
""",
    )

    with pytest.raises(ConfigError, match="Dataset file does not exist"):
        plan_suite(suite_path)
