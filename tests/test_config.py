from pathlib import Path

import pytest

from local_llm_eval.config import (
    BenchmarkConfig,
    ConfigError,
    ModelConfig,
    SuiteConfig,
    load_benchmark_config,
    load_model_config,
    load_suite_config,
)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_load_model_config(tmp_path: Path) -> None:
    path = write(
        tmp_path / "config" / "models" / "ollama.yaml",
        """
id: ollama-llama3
provider: openai_compatible
base_url: http://localhost:11434/v1
model: llama3.1:8b
api_key_env: LOCAL_LLM_API_KEY
generation:
  temperature: 0
  max_tokens: 512
""",
    )

    config = load_model_config(path)

    assert config == ModelConfig(
        id="ollama-llama3",
        provider="openai_compatible",
        base_url="http://localhost:11434/v1",
        model="llama3.1:8b",
        api_key_env="LOCAL_LLM_API_KEY",
        generation={"temperature": 0, "max_tokens": 512},
        path=path,
    )


def test_load_lm_eval_benchmark_config(tmp_path: Path) -> None:
    path = write(
        tmp_path / "config" / "benchmarks" / "mmlu.yaml",
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

    config = load_benchmark_config(path)

    assert config == BenchmarkConfig(
        id="mmlu",
        runner="lm-evaluation-harness",
        task="mmlu",
        dataset=None,
        dataset_format=None,
        evaluator=None,
        runner_params={"num_fewshot": 5},
        metrics=["acc"],
        path=path,
    )


def test_load_opencompass_benchmark_config(tmp_path: Path) -> None:
    path = write(
        tmp_path / "config" / "benchmarks" / "qa.yaml",
        """
id: my_internal_qa
runner: OpenCompass
dataset: datasets/my_internal_qa.json
dataset_format: chatml
evaluator: cascade
metrics:
  - exact_match
  - llm_judge
""",
    )

    config = load_benchmark_config(path)

    assert config.runner == "OpenCompass"
    assert config.dataset == "datasets/my_internal_qa.json"
    assert config.metrics == ["exact_match", "llm_judge"]


def test_load_suite_config(tmp_path: Path) -> None:
    path = write(
        tmp_path / "config" / "suites" / "baseline.yaml",
        """
id: baseline
models:
  - models/ollama.yaml
benchmarks:
  - benchmarks/mmlu.yaml
""",
    )

    config = load_suite_config(path)

    assert config == SuiteConfig(
        id="baseline",
        models=["models/ollama.yaml"],
        benchmarks=["benchmarks/mmlu.yaml"],
        path=path,
    )


def test_missing_required_field_raises_config_error(tmp_path: Path) -> None:
    path = write(
        tmp_path / "config" / "models" / "broken.yaml",
        """
id: broken
base_url: http://localhost:11434/v1
model: llama3.1:8b
""",
    )

    with pytest.raises(ConfigError, match="provider"):
        load_model_config(path)


def test_unknown_runner_raises_config_error(tmp_path: Path) -> None:
    path = write(
        tmp_path / "config" / "benchmarks" / "broken.yaml",
        """
id: broken
runner: unknown
task: broken
metrics:
  - acc
""",
    )

    with pytest.raises(ConfigError, match="runner"):
        load_benchmark_config(path)
