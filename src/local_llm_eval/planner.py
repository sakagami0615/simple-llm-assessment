from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from local_llm_eval.config import (
    BenchmarkConfig,
    ConfigError,
    ModelConfig,
    SuiteConfig,
    load_benchmark_config,
    load_model_config,
    load_suite_config,
)


@dataclass(frozen=True)
class EvaluationJob:
    """1つの model x benchmark 評価ジョブ。

    Attributes:
        model: 解決済みの model 設定。
        benchmark: 解決済みの benchmark 設定。
        output_name: runner の raw 出力に使う相対パス要素。
    """

    model: ModelConfig
    benchmark: BenchmarkConfig
    output_name: str


@dataclass(frozen=True)
class EvaluationPlan:
    """解決済み suite 設定と展開済み評価ジョブ。

    Attributes:
        suite: 解決済みの suite 設定。
        models: 解決済みの model 設定一覧。
        benchmarks: 解決済みの benchmark 設定一覧。
        jobs: 展開済みの model x benchmark ジョブ一覧。
    """

    suite: SuiteConfig
    models: list[ModelConfig]
    benchmarks: list[BenchmarkConfig]
    jobs: list[EvaluationJob]


def _resolve_reference(suite_path: Path, reference: str) -> Path:
    root = suite_path.parent.parent
    resolved = root / reference
    if not resolved.exists():
        raise ConfigError(f"Referenced file does not exist: {reference}")
    return resolved


def plan_suite(path: str | Path) -> EvaluationPlan:
    """suite ファイルを実行可能な評価ジョブへ解決する。

    Args:
        path: suite YAML ファイルのパス。

    Returns:
        解決済みの評価計画。

    Raises:
        ConfigError: 参照された model または benchmark ファイルを解決
            できない場合。
    """
    suite_path = Path(path)
    suite = load_suite_config(suite_path)
    models = [load_model_config(_resolve_reference(suite_path, item)) for item in suite.models]
    benchmarks = [
        load_benchmark_config(_resolve_reference(suite_path, item)) for item in suite.benchmarks
    ]
    jobs = [
        EvaluationJob(
            model=model,
            benchmark=benchmark,
            output_name=f"{model.id}/{benchmark.id}",
        )
        for model in models
        for benchmark in benchmarks
    ]
    return EvaluationPlan(suite=suite, models=models, benchmarks=benchmarks, jobs=jobs)
