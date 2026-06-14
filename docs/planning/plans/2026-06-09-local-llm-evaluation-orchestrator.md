# Local LLM Evaluation Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ローカル LLM サーバを対象に、suite YAML から lm-evaluation-harness / OpenCompass の評価ジョブを一括実行できる CLI を作る。

**Architecture:** `src/local_llm_eval/` に設定読み込み、検証、ジョブ展開、runner adapter、CLI を分けて実装する。評価資産は `models/`、`benchmarks/`、`suites/`、`datasets/`、`runs/` に置き、フレームワーク別には分断しない。外部評価フレームワークの推論・採点機能を呼び出し、このリポジトリは薄いオーケストレーションと結果保存を担当する。

**Tech Stack:** Python 3.14、Poetry、PyYAML、pytest、lm-evaluation-harness、OpenCompass、OpenAI互換ローカルAPI。

---

## 対象ファイル

- 作成: `src/local_llm_eval/__init__.py`
- 作成: `src/local_llm_eval/cli.py`
- 作成: `src/local_llm_eval/config.py`
- 作成: `src/local_llm_eval/planner.py`
- 作成: `src/local_llm_eval/executor.py`
- 作成: `src/local_llm_eval/results.py`
- 作成: `src/local_llm_eval/runners/__init__.py`
- 作成: `src/local_llm_eval/runners/lm_evaluation_harness.py`
- 作成: `src/local_llm_eval/runners/opencompass.py`
- 作成: `models/ollama-llama3.yaml`
- 作成: `models/vllm-qwen2-7b.yaml`
- 作成: `benchmarks/mmlu.yaml`
- 作成: `benchmarks/my_internal_qa.yaml`
- 作成: `suites/baseline.yaml`
- 作成: `datasets/my_internal_qa.json`
- 変更: `pyproject.toml`
- 変更: `README.md`
- 変更: `ARCHITECTURE.md`
- 削除: `app/llm_qa_app/`
- 削除: `app/llm_eval/`
- 削除: 既存の OpenAI / DeepEval 前提テスト
- テスト作成: `tests/test_config.py`
- テスト作成: `tests/test_planner.py`
- テスト作成: `tests/test_runners.py`
- テスト作成: `tests/test_executor.py`
- テスト作成: `tests/test_cli.py`
- テスト作成: `tests/test_project_structure.py`

## Task 1: パッケージ構成と依存関係を刷新する

**Files:**
- Modify: `pyproject.toml`
- Create: `src/local_llm_eval/__init__.py`
- Create: `src/local_llm_eval/runners/__init__.py`
- Test: `tests/test_project_structure.py`

- [ ] **Step 1: プロジェクト構成テストを書く**

`tests/test_project_structure.py` を作成する。

```python
from pathlib import Path


def test_new_package_layout_exists() -> None:
    root = Path.cwd()
    assert (root / "src" / "local_llm_eval" / "__init__.py").exists()
    assert (root / "src" / "local_llm_eval" / "cli.py").exists()
    assert (root / "src" / "local_llm_eval" / "config.py").exists()
    assert (root / "src" / "local_llm_eval" / "planner.py").exists()
    assert (root / "src" / "local_llm_eval" / "runners").is_dir()


def test_old_openai_deepeval_packages_are_removed() -> None:
    root = Path.cwd()
    assert not (root / "app" / "llm_qa_app").exists()
    assert not (root / "app" / "llm_eval").exists()
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_project_structure.py -q`

Expected: `src/local_llm_eval/cli.py` などが存在しないため FAIL。

- [ ] **Step 3: パッケージの空ファイルを作る**

作成する。

```python
# src/local_llm_eval/__init__.py
"""Local LLM evaluation orchestrator."""
```

```python
# src/local_llm_eval/runners/__init__.py
"""Evaluation framework adapters."""
```

後続タスクで中身を入れるため、以下のファイルも空実装で作成する。

```python
# src/local_llm_eval/cli.py
def main() -> int:
    return 0
```

```python
# src/local_llm_eval/config.py
class ConfigError(ValueError):
    """Configuration validation failed."""
```

```python
# src/local_llm_eval/planner.py
from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationJob:
    model_id: str
    benchmark_id: str
    runner: str
```

- [ ] **Step 4: `pyproject.toml` を新構成へ更新する**

`pyproject.toml` の主な内容を以下の形にする。

```toml
[project]
name = "local-llm-eval"
version = "0.1.0"
description = "Local LLM evaluation orchestrator for lm-evaluation-harness and OpenCompass"
authors = [
    {name = "sakagami0615", email = "sakagami0615@gmail.com"}
]
readme = "README.md"
requires-python = ">=3.14,<4.0"
dependencies = [
    "pyyaml>=6.0.0",
]

[project.scripts]
local-llm-eval = "local_llm_eval.cli:main"

[tool.poetry]
packages = [
    {include = "local_llm_eval", from = "src"},
]

[tool.poetry.group.dev.dependencies]
pytest = ">=8.0.0"

[tool.poetry.group.eval.dependencies]
lm-eval = ">=0.4.0"
opencompass = ">=0.5.0"
datasets = ">=2.0.0"

[tool.pytest.ini_options]
pythonpath = [".", "src"]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

- [ ] **Step 5: 古い OpenAI / DeepEval パッケージを削除する**

削除対象:

```text
app/llm_qa_app/
app/llm_eval/
tests/test_llm_eval.py
tests/test_eval_config.py
tests/test_eval_datasets.py
tests/test_eval_reports.py
tests/test_convert_hf_dataset.py
scripts/convert_hf_dataset.py
data/eval_cases/qa_sample.jsonl
```

既に削除済み、または存在しないファイルはそのままでよい。ユーザー作業由来の不明な差分は戻さない。

- [ ] **Step 6: 構成テストを通す**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_project_structure.py -q`

Expected: PASS。

## Task 2: YAML 設定モデルと検証を実装する

**Files:**
- Modify: `src/local_llm_eval/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: 設定読み込みテストを書く**

`tests/test_config.py` を作成する。

```python
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
        tmp_path / "models" / "ollama.yaml",
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
        tmp_path / "benchmarks" / "mmlu.yaml",
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
        tmp_path / "benchmarks" / "qa.yaml",
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
        tmp_path / "suites" / "baseline.yaml",
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
        tmp_path / "models" / "broken.yaml",
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
        tmp_path / "benchmarks" / "broken.yaml",
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
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_config.py -q`

Expected: `load_model_config` などが未定義で FAIL。

- [ ] **Step 3: 設定 dataclass と loader を実装する**

`src/local_llm_eval/config.py` を以下の内容にする。

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Configuration validation failed."""


@dataclass(frozen=True)
class ModelConfig:
    id: str
    provider: str
    base_url: str
    model: str
    api_key_env: str | None
    generation: dict[str, Any]
    path: Path


@dataclass(frozen=True)
class BenchmarkConfig:
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
    config_path = Path(path)
    data = _read_yaml(config_path)
    generation = data.get("generation", {})
    if not isinstance(generation, dict):
        raise ConfigError(f"Field 'generation' must be a mapping in {config_path}")
    provider = str(_required(data, "provider", config_path))
    if provider != "openai_compatible":
        raise ConfigError(f"Unsupported provider '{provider}' in {config_path}")
    return ModelConfig(
        id=str(_required(data, "id", config_path)),
        provider=provider,
        base_url=str(_required(data, "base_url", config_path)),
        model=str(_required(data, "model", config_path)),
        api_key_env=data.get("api_key_env"),
        generation=generation,
        path=config_path,
    )


def load_benchmark_config(path: str | Path) -> BenchmarkConfig:
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
    config_path = Path(path)
    data = _read_yaml(config_path)
    return SuiteConfig(
        id=str(_required(data, "id", config_path)),
        models=_string_list(data, "models", config_path),
        benchmarks=_string_list(data, "benchmarks", config_path),
        path=config_path,
    )
```

- [ ] **Step 4: 設定テストを通す**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_config.py -q`

Expected: PASS。

## Task 3: suite を評価ジョブへ展開する planner を実装する

**Files:**
- Modify: `src/local_llm_eval/planner.py`
- Test: `tests/test_planner.py`

- [ ] **Step 1: planner テストを書く**

`tests/test_planner.py` を作成する。

```python
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
        root / "models" / "ollama.yaml",
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
        root / "benchmarks" / "mmlu.yaml",
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
        root / "suites" / "baseline.yaml",
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
        tmp_path / "suites" / "broken.yaml",
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
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_planner.py -q`

Expected: `plan_suite` が未定義、または dataclass が不足して FAIL。

- [ ] **Step 3: planner を実装する**

`src/local_llm_eval/planner.py` を以下の内容にする。

```python
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
    model: ModelConfig
    benchmark: BenchmarkConfig
    output_name: str


@dataclass(frozen=True)
class EvaluationPlan:
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
```

- [ ] **Step 4: planner テストを通す**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_planner.py -q`

Expected: PASS。

## Task 4: runner ごとのコマンド生成を実装する

**Files:**
- Create: `src/local_llm_eval/runners/lm_evaluation_harness.py`
- Create: `src/local_llm_eval/runners/opencompass.py`
- Test: `tests/test_runners.py`

- [ ] **Step 1: runner コマンド生成テストを書く**

`tests/test_runners.py` を作成する。

```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_runners.py -q`

Expected: runner module が存在しないため FAIL。

- [ ] **Step 3: lm-evaluation-harness runner を実装する**

`src/local_llm_eval/runners/lm_evaluation_harness.py` を作成する。

```python
from __future__ import annotations

from pathlib import Path

from local_llm_eval.planner import EvaluationJob


def build_lm_eval_command(job: EvaluationJob, output_dir: Path) -> list[str]:
    model_args = ",".join(
        [
            f"base_url={job.model.base_url}",
            f"model={job.model.model}",
            "tokenized_requests=False",
        ]
    )
    command = [
        "lm-eval",
        "--model",
        "local-chat-completions",
        "--tasks",
        str(job.benchmark.task),
        "--model_args",
        model_args,
        "--output_path",
        str(output_dir),
        "--log_samples",
        "--apply_chat_template",
    ]
    num_fewshot = job.benchmark.runner_params.get("num_fewshot")
    if num_fewshot is not None:
        command.extend(["--num_fewshot", str(num_fewshot)])
    max_tokens = job.model.generation.get("max_tokens")
    temperature = job.model.generation.get("temperature")
    gen_kwargs = []
    if max_tokens is not None:
        gen_kwargs.append(f"max_gen_toks={max_tokens}")
    if temperature is not None:
        gen_kwargs.append(f"temperature={temperature}")
    if gen_kwargs:
        command.extend(["--gen_kwargs", ",".join(gen_kwargs)])
    return command
```

- [ ] **Step 4: OpenCompass runner を実装する**

`src/local_llm_eval/runners/opencompass.py` を作成する。

```python
from __future__ import annotations

from pathlib import Path

from local_llm_eval.planner import EvaluationJob


def build_opencompass_command(job: EvaluationJob, output_dir: Path) -> list[str]:
    config_path = output_dir / "opencompass_config.py"
    output_dir.mkdir(parents=True, exist_ok=True)
    config_path.write_text(_render_config(job), encoding="utf-8")
    return [
        "opencompass",
        "--config",
        str(config_path),
        "--work-dir",
        str(output_dir),
    ]


def _render_config(job: EvaluationJob) -> str:
    dataset_path = job.benchmark.dataset or ""
    max_out_len = job.model.generation.get("max_tokens", 512)
    temperature = job.model.generation.get("temperature", 0)
    api_key_expr = "os.environ.get(%r, 'EMPTY')" % (job.model.api_key_env or "LOCAL_LLM_API_KEY")
    return f'''import os

from opencompass.models import OpenAI

models = [
    dict(
        type=OpenAI,
        path={job.model.model!r},
        openai_api_base={job.model.base_url!r},
        key={api_key_expr},
        abbr={job.model.id!r},
        max_out_len={max_out_len!r},
        batch_size=1,
        temperature={temperature!r},
        run_cfg=dict(num_gpus=0),
    )
]

datasets = [
    dict(
        abbr={job.benchmark.id!r},
        path={dataset_path!r},
        type={job.benchmark.dataset_format!r},
        evaluator={job.benchmark.evaluator!r},
    )
]
'''
```

- [ ] **Step 5: runner テストを通す**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_runners.py -q`

Expected: PASS。

## Task 5: 実行・dry-run・summary 保存を実装する

**Files:**
- Create: `src/local_llm_eval/executor.py`
- Create: `src/local_llm_eval/results.py`
- Test: `tests/test_executor.py`

- [ ] **Step 1: executor テストを書く**

`tests/test_executor.py` を作成する。

```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_executor.py -q`

Expected: `execute_plan` が未定義で FAIL。

- [ ] **Step 3: results helper を実装する**

`src/local_llm_eval/results.py` を作成する。

```python
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
```

- [ ] **Step 4: executor を実装する**

`src/local_llm_eval/executor.py` を作成する。

```python
from __future__ import annotations

import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from local_llm_eval.planner import EvaluationPlan
from local_llm_eval.results import write_json
from local_llm_eval.runners.lm_evaluation_harness import build_lm_eval_command
from local_llm_eval.runners.opencompass import build_opencompass_command


CommandRunner = Callable[[list[str], Path, dict[str, str]], int]


@dataclass(frozen=True)
class ExecutionResult:
    run_dir: Path


def default_command_runner(command: list[str], cwd: Path, env: dict[str, str]) -> int:
    completed = subprocess.run(command, cwd=cwd, env=env, check=False)
    return completed.returncode


def execute_plan(
    plan: EvaluationPlan,
    runs_dir: Path = Path("runs"),
    dry_run: bool = False,
    command_runner: CommandRunner = default_command_runner,
) -> ExecutionResult:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    run_dir = runs_dir / f"{timestamp}-{plan.suite.id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, object] = {
        "suite_id": plan.suite.id,
        "run_dir": str(run_dir),
        "dry_run": dry_run,
        "jobs": [],
    }

    write_json(run_dir / "run.yaml.json", {"plan": asdict(plan)})

    for job in plan.jobs:
        job_dir = run_dir / "raw" / job.output_name
        job_dir.mkdir(parents=True, exist_ok=True)
        command = _build_command(job, job_dir)
        if dry_run:
            status = "skipped"
            exit_code = None
        else:
            exit_code = command_runner(command, Path.cwd(), os.environ.copy())
            status = "success" if exit_code == 0 else "failed"
        summary["jobs"].append(
            {
                "model_id": job.model.id,
                "benchmark_id": job.benchmark.id,
                "runner": job.benchmark.runner,
                "status": status,
                "exit_code": exit_code,
                "command": command,
                "raw_output_path": str(job_dir),
            }
        )

    write_json(run_dir / "summary.json", summary)
    return ExecutionResult(run_dir=run_dir)


def _build_command(job, job_dir: Path) -> list[str]:
    if job.benchmark.runner == "lm-evaluation-harness":
        return build_lm_eval_command(job, job_dir)
    if job.benchmark.runner == "OpenCompass":
        return build_opencompass_command(job, job_dir)
    raise ValueError(f"Unsupported runner: {job.benchmark.runner}")
```

- [ ] **Step 5: executor テストを通す**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_executor.py -q`

Expected: PASS。

## Task 6: CLI を実装する

**Files:**
- Modify: `src/local_llm_eval/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: CLI テストを書く**

`tests/test_cli.py` を作成する。

```python
from pathlib import Path

from local_llm_eval.cli import main


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_files(root: Path) -> Path:
    write(
        root / "models" / "ollama.yaml",
        """
id: ollama-llama3
provider: openai_compatible
base_url: http://localhost:11434/v1
model: llama3.1:8b
generation: {}
""",
    )
    write(
        root / "benchmarks" / "mmlu.yaml",
        """
id: mmlu
runner: lm-evaluation-harness
task: mmlu
metrics:
  - acc
""",
    )
    suite = root / "suites" / "baseline.yaml"
    write(
        suite,
        """
id: baseline
models:
  - models/ollama.yaml
benchmarks:
  - benchmarks/mmlu.yaml
""",
    )
    return suite


def test_validate_command_returns_success(tmp_path: Path) -> None:
    suite = create_files(tmp_path)

    assert main(["validate", str(suite)]) == 0


def test_run_dry_run_returns_success(tmp_path: Path) -> None:
    suite = create_files(tmp_path)

    assert main(["run", str(suite), "--dry-run", "--runs-dir", str(tmp_path / "runs")]) == 0
    assert any((tmp_path / "runs").iterdir())
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_cli.py -q`

Expected: CLI 引数処理が未実装で FAIL。

- [ ] **Step 3: CLI を実装する**

`src/local_llm_eval/cli.py` を以下の内容にする。

```python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from local_llm_eval.config import ConfigError
from local_llm_eval.executor import execute_plan
from local_llm_eval.planner import plan_suite


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="local-llm-eval")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("suite")

    run = subparsers.add_parser("run")
    run.add_argument("suite")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--runs-dir", default="runs")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        plan = plan_suite(args.suite)
        if args.command == "validate":
            print(f"valid: {plan.suite.id}")
            return 0
        if args.command == "run":
            result = execute_plan(plan, runs_dir=Path(args.runs_dir), dry_run=args.dry_run)
            print(f"run_dir: {result.run_dir}")
            return 0
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: CLI テストを通す**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_cli.py -q`

Expected: PASS。

## Task 7: サンプル設定とドキュメントを更新する

**Files:**
- Create: `models/ollama-llama3.yaml`
- Create: `models/vllm-qwen2-7b.yaml`
- Create: `benchmarks/mmlu.yaml`
- Create: `benchmarks/my_internal_qa.yaml`
- Create: `suites/baseline.yaml`
- Create: `datasets/my_internal_qa.json`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: サンプル model YAML を作る**

`models/ollama-llama3.yaml`:

```yaml
id: ollama-llama3
provider: openai_compatible
base_url: http://localhost:11434/v1
model: llama3.1:8b
api_key_env: LOCAL_LLM_API_KEY
generation:
  temperature: 0
  max_tokens: 512
```

`models/vllm-qwen2-7b.yaml`:

```yaml
id: vllm-qwen2-7b
provider: openai_compatible
base_url: http://localhost:8000/v1
model: Qwen/Qwen2.5-7B-Instruct
api_key_env: LOCAL_LLM_API_KEY
generation:
  temperature: 0
  max_tokens: 512
```

- [ ] **Step 2: サンプル benchmark YAML を作る**

`benchmarks/mmlu.yaml`:

```yaml
id: mmlu
runner: lm-evaluation-harness
task: mmlu
runner_params:
  num_fewshot: 5
metrics:
  - acc
```

`benchmarks/my_internal_qa.yaml`:

```yaml
id: my_internal_qa
runner: OpenCompass
dataset: datasets/my_internal_qa.json
dataset_format: chatml
evaluator: cascade
metrics:
  - exact_match
  - llm_judge
```

- [ ] **Step 3: サンプル suite と dataset を作る**

`suites/baseline.yaml`:

```yaml
id: baseline
models:
  - models/ollama-llama3.yaml
benchmarks:
  - benchmarks/mmlu.yaml
```

`datasets/my_internal_qa.json`:

```json
[
  {
    "question": [
      {
        "role": "user",
        "content": "日本の首都はどこですか？"
      }
    ],
    "answer": [
      "東京"
    ]
  }
]
```

- [ ] **Step 4: README を日本語で更新する**

`README.md` は以下のセクションを含める。

````markdown
# local-llm-eval

ローカル LLM サーバを対象に、lm-evaluation-harness と OpenCompass の評価を一括実行するための薄いオーケストレーターです。

## セットアップ

```bash
poetry install --with eval
```

## 前提

Ollama、vLLM、LM Studio、llama.cpp server などのローカル LLM サーバは事前に起動しておきます。このツールはサーバ起動を管理しません。

## 実行

```bash
poetry run local-llm-eval validate suites/baseline.yaml
poetry run local-llm-eval run suites/baseline.yaml --dry-run
poetry run local-llm-eval run suites/baseline.yaml
```

## 構成

- `models/`: 1モデル接続 = 1 YAML
- `benchmarks/`: 1ベンチマーク = 1 YAML
- `suites/`: 実行する model と benchmark の束
- `datasets/`: 自作データセット
- `runs/`: 実行結果
````

- [ ] **Step 5: ARCHITECTURE を日本語で更新する**

`ARCHITECTURE.md` は以下の内容を含める。

````markdown
# local-llm-eval Architecture

このリポジトリは、ローカル LLM 評価ジョブを suite 中心に管理します。

```text
suite YAML
  -> model YAML
  -> benchmark YAML
  -> runner adapter
  -> lm-evaluation-harness / OpenCompass
  -> runs/
```

評価フレームワークは実行バックエンドとして扱い、データセットや実行結果はフレームワーク別に大きく分断しません。
````

- [ ] **Step 6: サンプル設定を validate する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run python -m local_llm_eval.cli validate suites/baseline.yaml`

Expected: `valid: baseline`

## Task 8: 全体検証を行う

**Files:**
- Modify as needed: files changed in previous tasks only

- [ ] **Step 1: 全テストを実行する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q`

Expected: PASS。

- [ ] **Step 2: dry-run を実行する**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval run suites/baseline.yaml --dry-run`

Expected: `runs/` 配下に run ディレクトリが作成され、`summary.json` に `status: skipped` と `lm-eval` コマンドが記録される。

- [ ] **Step 3: OpenAI / DeepEval 参照が残っていないか確認する**

Run: `rg -n "DeepEval|deepeval|OPENAI_API_KEY|llm_qa_app|llm_eval" README.md ARCHITECTURE.md pyproject.toml src tests`

Expected: 以前の実装由来の参照が出ない。OpenAI互換APIの説明として必要な `openai_compatible` は残ってよい。

## Self-Review

- Spec coverage: suite中心構成、1 model = 1 YAML、1 benchmark = 1 YAML、runner正式名称、ワンコマンド実行、dry-run、結果保存、古い実装削除、Poetry eval group を各タスクに割り当てた。
- Placeholder scan: 禁止されている未確定表現を避け、各コード変更ステップに具体的なコードを置いた。
- Type consistency: `ModelConfig`、`BenchmarkConfig`、`SuiteConfig`、`EvaluationJob`、`EvaluationPlan` の名称を以降のタスクで統一した。
