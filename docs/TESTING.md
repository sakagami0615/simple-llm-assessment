# Testing

このドキュメントは、`tests/` 配下のテストが何を確認しているかをまとめます。

## 実行方法

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q
```

`PYTHONDONTWRITEBYTECODE=1` は、`__pycache__/` を生成しないために指定します。`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` は、外部 pytest plugin の自動読み込みによる副作用を避けるために指定します。

## テスト一覧

| ファイル | 確認内容 |
| --- | --- |
| `tests/test_config.py` | model / benchmark / suite YAML の読み込み、dataclass への変換、必須項目不足や未知 runner の `ConfigError` を確認します。 |
| `tests/test_planner.py` | suite YAML から model x benchmark の `EvaluationJob` へ展開できること、参照ファイル欠落時に `ConfigError` になることを確認します。 |
| `tests/test_runners.py` | lm-evaluation-harness / OpenCompass 向けの外部コマンド生成を確認します。OpenCompass では一時 config ファイルが生成されることも確認します。 |
| `tests/test_executor.py` | dry-run 時に外部コマンドを実行せず `summary.json` を保存すること、外部コマンド失敗時に `failed` と終了コードを summary に残すことを確認します。 |
| `tests/test_cli.py` | `validate` と `run --dry-run` の CLI エントリーポイントが成功終了することを確認します。 |
| `tests/test_project_structure.py` | パッケージ構成、旧パッケージの削除、生成物の非混入、公開 API の docstring 付与を確認します。 |

## テストで実行しないこと

- lm-evaluation-harness / OpenCompass の実評価は実行しません。
- ローカル LLM サーバへの通信は行いません。
- `runs/` 配下の実行結果を成果物として扱いません。

外部評価フレームワークやローカル LLM サーバを含む検証は、別途実行環境を用意して行います。
