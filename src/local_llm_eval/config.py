from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """設定ファイルの読み込みまたは検証に失敗したときに送出する例外。"""


@dataclass(frozen=True)
class ModelConfig:
    """1つのローカル LLM モデルサーバーへの接続設定。

    Attributes:
        id: リポジトリ内で使うモデル識別子。
        provider: モデル接続方式。現在は `openai_compatible`。
        base_url: ローカルモデルサーバー API のベース URL。
        model: ローカルサーバーへ渡すモデル名。
        api_key_env: API キーを格納する任意の環境変数名。
        generation: temperature や max tokens などの生成パラメータ。
        path: 読み込み元 YAML ファイルのパス。
    """

    id: str
    provider: str
    base_url: str
    model: str
    api_key_env: str | None
    generation: dict[str, Any]
    path: Path


@dataclass(frozen=True)
class BenchmarkConfig:
    """runner adapter が利用する評価ベンチマーク設定。

    Attributes:
        id: リポジトリ内で使うベンチマーク識別子。
        runner: 評価 runner の正式名称。
        task: 必要な場合に指定する runner のタスク名。
        dataset: 必要な場合に指定するデータセットパス。
        dataset_format: 必要な場合に指定するデータセット形式名。
        evaluator: 必要な場合に指定する evaluator 名。
        runner_params: runner 固有のパラメータ。
        metrics: ベンチマークから期待する metric 名。
        path: 読み込み元 YAML ファイルのパス。
    """

    id: str
    runner: str
    task: str | None
    dataset: str | None
    dataset_format: str | None
    evaluator: str | None
    runner_params: dict[str, Any]
    metrics: list[str]
    path: Path


@dataclass(frozen=True)
class SuiteConfig:
    """実行可能な model / benchmark 設定参照のまとまり。

    Attributes:
        id: リポジトリ内で使う suite 識別子。
        models: model 設定ファイルへの参照。
        benchmarks: benchmark 設定ファイルへの参照。
        path: 読み込み元 YAML ファイルのパス。
    """

    id: str
    models: list[str]
    benchmarks: list[str]
    path: Path


SUPPORTED_RUNNERS = {"lm-evaluation-harness", "OpenCompass"}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {path}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ConfigError(f"Config file must contain a mapping: {path}")
    return loaded


def _required(data: dict[str, Any], key: str, path: Path) -> Any:
    value = data.get(key)
    if value is None:
        raise ConfigError(f"Missing required field '{key}' in {path}")
    return value


def _string_list(data: dict[str, Any], key: str, path: Path) -> list[str]:
    value = _required(data, key, path)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"Field '{key}' must be a list of strings in {path}")
    return value


def load_model_config(path: str | Path) -> ModelConfig:
    """model YAML ファイルを読み込み、検証する。

    Args:
        path: model YAML ファイルのパス。

    Returns:
        検証済みの model 設定。

    Raises:
        ConfigError: ファイルが存在しない、不正な形式、または未対応の設定で
            ある場合。
    """
    config_path = Path(path)
    data = _read_yaml(config_path)
    generation = data.get("generation", {})
    if not isinstance(generation, dict):
        raise ConfigError(f"Field 'generation' must be a mapping in {config_path}")
    provider = str(_required(data, "provider", config_path))
    if provider != "openai_compatible":
        raise ConfigError(f"Unsupported provider '{provider}' in {config_path}")
    api_key_env = data.get("api_key_env")
    if api_key_env is not None and not isinstance(api_key_env, str):
        raise ConfigError(f"Field 'api_key_env' must be a string in {config_path}")
    return ModelConfig(
        id=str(_required(data, "id", config_path)),
        provider=provider,
        base_url=str(_required(data, "base_url", config_path)),
        model=str(_required(data, "model", config_path)),
        api_key_env=api_key_env,
        generation=generation,
        path=config_path,
    )


def load_benchmark_config(path: str | Path) -> BenchmarkConfig:
    """benchmark YAML ファイルを読み込み、検証する。

    Args:
        path: benchmark YAML ファイルのパス。

    Returns:
        検証済みの benchmark 設定。

    Raises:
        ConfigError: ファイルが存在しない、不正な形式、または未対応の runner
            を指定している場合。
    """
    config_path = Path(path)
    data = _read_yaml(config_path)
    runner = str(_required(data, "runner", config_path))
    if runner not in SUPPORTED_RUNNERS:
        raise ConfigError(f"Unsupported runner '{runner}' in {config_path}")
    metrics = data.get("metrics", [])
    if not isinstance(metrics, list) or not all(isinstance(item, str) for item in metrics):
        raise ConfigError(f"Field 'metrics' must be a list of strings in {config_path}")
    runner_params = data.get("runner_params", {})
    if not isinstance(runner_params, dict):
        raise ConfigError(f"Field 'runner_params' must be a mapping in {config_path}")
    return BenchmarkConfig(
        id=str(_required(data, "id", config_path)),
        runner=runner,
        task=data.get("task"),
        dataset=data.get("dataset"),
        dataset_format=data.get("dataset_format"),
        evaluator=data.get("evaluator"),
        runner_params=runner_params,
        metrics=metrics,
        path=config_path,
    )


def load_suite_config(path: str | Path) -> SuiteConfig:
    """suite YAML ファイルを読み込み、検証する。

    Args:
        path: suite YAML ファイルのパス。

    Returns:
        検証済みの suite 設定。

    Raises:
        ConfigError: ファイルが存在しない、不正な形式、または参照情報が
            不足している場合。
    """
    config_path = Path(path)
    data = _read_yaml(config_path)
    return SuiteConfig(
        id=str(_required(data, "id", config_path)),
        models=_string_list(data, "models", config_path),
        benchmarks=_string_list(data, "benchmarks", config_path),
        path=config_path,
    )
