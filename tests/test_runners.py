from pathlib import Path

from local_llm_eval.config import BenchmarkConfig, ModelConfig
from local_llm_eval.planner import EvaluationJob
from local_llm_eval.runners.lm_evaluation_harness import build_lm_eval_command
from local_llm_eval.runners.opencompass import build_opencompass_command


def model() -> ModelConfig:
    return ModelConfig(
        id="ollama-llama3",
        provider="openai_compatible",
        base_url="http://localhost:11434/v1",
        model="llama3.1:8b",
        api_key_env="LOCAL_LLM_API_KEY",
        generation={"temperature": 0, "max_tokens": 512},
        path=Path("models/ollama.yaml"),
    )


def test_build_lm_eval_command_for_openai_compatible_chat_api(tmp_path: Path) -> None:
    benchmark = BenchmarkConfig(
        id="mmlu",
        runner="lm-evaluation-harness",
        task="mmlu",
        dataset=None,
        dataset_format=None,
        evaluator=None,
        runner_params={"num_fewshot": 5},
        metrics=["acc"],
        path=Path("benchmarks/mmlu.yaml"),
    )
    job = EvaluationJob(model=model(), benchmark=benchmark, output_name="ollama-llama3/mmlu")

    command = build_lm_eval_command(job, tmp_path)

    assert command[:4] == ["lm-eval", "--model", "local-chat-completions", "--tasks"]
    assert "mmlu" in command
    assert "--num_fewshot" in command
    assert "5" in command
    assert "--output_path" in command
    assert str(tmp_path) in command
    assert any("base_url=http://localhost:11434/v1" in item for item in command)
    assert any("model=llama3.1:8b" in item for item in command)
    assert "--apply_chat_template" in command


def test_build_opencompass_command_creates_generated_config_path(tmp_path: Path) -> None:
    benchmark = BenchmarkConfig(
        id="my_internal_qa",
        runner="OpenCompass",
        task=None,
        dataset="datasets/my_internal_qa.json",
        dataset_format="chatml",
        evaluator="cascade",
        runner_params={},
        metrics=["exact_match", "llm_judge"],
        path=Path("benchmarks/my_internal_qa.yaml"),
    )
    job = EvaluationJob(model=model(), benchmark=benchmark, output_name="ollama-llama3/my_internal_qa")

    command = build_opencompass_command(job, tmp_path)

    assert command[0] == "opencompass"
    assert "--config" in command
    assert str(tmp_path / "opencompass_config.py") in command
    assert "--work-dir" in command
    assert str(tmp_path) in command
    assert (tmp_path / "opencompass_config.py").exists()
