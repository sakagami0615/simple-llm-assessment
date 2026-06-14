from pathlib import Path

from local_llm_eval import cli, config, executor, planner, results
from local_llm_eval.runners import lm_evaluation_harness, opencompass


def test_new_package_layout_exists() -> None:
    root = Path.cwd()
    assert (root / "src" / "local_llm_eval" / "__init__.py").exists()
    assert (root / "src" / "local_llm_eval" / "cli.py").exists()
    assert (root / "src" / "local_llm_eval" / "config.py").exists()
    assert (root / "src" / "local_llm_eval" / "planner.py").exists()
    assert (root / "src" / "local_llm_eval" / "runners").is_dir()


def test_old_packages_are_removed() -> None:
    root = Path.cwd()
    old_qa_package = "llm" + "_qa_app"
    old_eval_package = "llm" + "_eval"
    assert not (root / "app" / old_qa_package).exists()
    assert not (root / "app" / old_eval_package).exists()


def test_generated_outputs_are_ignored() -> None:
    root = Path.cwd()
    ignore_patterns = set((root / ".gitignore").read_text(encoding="utf-8").splitlines())
    assert "__pycache__/" in ignore_patterns
    assert ".pytest_cache/" in ignore_patterns
    assert "runs/" in ignore_patterns


def test_public_code_has_docstrings() -> None:
    public_objects = [
        cli.build_parser,
        cli.main,
        config.ConfigError,
        config.ModelConfig,
        config.BenchmarkConfig,
        config.SuiteConfig,
        config.load_model_config,
        config.load_benchmark_config,
        config.load_suite_config,
        planner.EvaluationJob,
        planner.EvaluationPlan,
        planner.plan_suite,
        executor.ExecutionResult,
        executor.default_command_runner,
        executor.execute_plan,
        results.write_json,
        lm_evaluation_harness.build_lm_eval_command,
        opencompass.build_opencompass_command,
    ]
    missing = [item.__qualname__ for item in public_objects if not item.__doc__]
    assert missing == []
