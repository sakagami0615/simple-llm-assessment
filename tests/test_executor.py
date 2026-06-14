from pathlib import Path

from local_llm_eval.config import BenchmarkConfig, ModelConfig, SuiteConfig
from local_llm_eval.executor import execute_plan
from local_llm_eval.planner import EvaluationJob, EvaluationPlan


def make_plan() -> EvaluationPlan:
    model = ModelConfig(
        id="ollama-llama3",
        provider="openai_compatible",
        base_url="http://localhost:11434/v1",
        model="llama3.1:8b",
        api_key_env=None,
        generation={},
        path=Path("models/ollama.yaml"),
    )
    benchmark = BenchmarkConfig(
        id="mmlu",
        runner="lm-evaluation-harness",
        task="mmlu",
        dataset=None,
        dataset_format=None,
        evaluator=None,
        runner_params={},
        metrics=["acc"],
        path=Path("benchmarks/mmlu.yaml"),
    )
    job = EvaluationJob(model=model, benchmark=benchmark, output_name="ollama-llama3/mmlu")
    return EvaluationPlan(
        suite=SuiteConfig(
            id="baseline",
            models=["models/ollama.yaml"],
            benchmarks=["benchmarks/mmlu.yaml"],
            path=Path("suites/baseline.yaml"),
        ),
        models=[model],
        benchmarks=[benchmark],
        jobs=[job],
    )


def test_execute_plan_dry_run_writes_summary_without_running(tmp_path: Path) -> None:
    result = execute_plan(make_plan(), runs_dir=tmp_path, dry_run=True)

    assert result.run_dir.exists()
    assert (result.run_dir / "summary.json").exists()
    summary = (result.run_dir / "summary.json").read_text(encoding="utf-8")
    assert '"status": "skipped"' in summary
    assert "lm-eval" in summary


def test_execute_plan_continues_after_failed_command(tmp_path: Path) -> None:
    result = execute_plan(
        make_plan(),
        runs_dir=tmp_path,
        dry_run=False,
        command_runner=lambda command, cwd, env: 7,
    )

    summary = (result.run_dir / "summary.json").read_text(encoding="utf-8")
    assert '"status": "failed"' in summary
    assert '"exit_code": 7' in summary
