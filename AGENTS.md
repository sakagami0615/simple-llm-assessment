# AGENTS.md

## プロジェクト概要

このリポジトリは、ローカル LLM 評価用の `local-llm-eval` CLI を提供する

## プロジェクトルール

- OpenAI などのホステッドモデルプロバイダーは使わない。
- モデル接続は OpenAI 互換 API を提供するローカルサーバを前提にする。
- ローカル LLM サーバの起動はこのツールでは管理しない。
- モデル推論や採点ロジックは、可能な限り lm-evaluation-harness / OpenCompass に委譲する。
- Git 操作はユーザーから明示的に依頼されない限り行わない。
- プロジェクトでは日本語を扱う。

## 実装ルール

- Python パッケージは `src/local_llm_eval/` 配下に実装する。
- 設定ファイルは YAML を基本にする。
- `runner` 名はツールの正式名称を使う。
  - `lm-evaluation-harness`
  - `OpenCompass`
- 1 model = 1 YAML、1 benchmark = 1 YAML とし、suite YAML がそれらを参照する。
- `runs/`、`__pycache__/`、`.pytest_cache/` などの生成物は成果物として扱わない。

## コーディング規約

- PEP8に準拠する。
- 型ヒントと docstring (GoogleStyle) を付ける。
- 日本語文字列を扱うため、ファイル読み書きでは UTF-8 を明示する。
- JSON 出力では、必要がない限り日本語をエスケープせず `ensure_ascii=False` を使う。
- 日本語を含むテストデータやサンプルデータを壊さない。
- dataclass を使える設定モデル・計画モデルでは dataclass を優先する。
- ファイルごとの責務を小さく保つ。
- 外部コマンド実行は直接埋め込まず、テストで差し替え可能な形にする。
- YAML 読み込み時は必須項目と runner 名を検証し、失敗時は `ConfigError` を使う。
- テストでは重い外部評価フレームワークを実行しない。
- コメントは、処理意図がコードから読み取りにくい箇所にだけ短く書く。

## 検証コマンド

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval validate config/suites/baseline.yaml
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval run config/suites/baseline.yaml --dry-run
```
