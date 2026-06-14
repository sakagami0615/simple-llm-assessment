# CLI 実行と結果保存

## 元になった要求

- Epic: [ローカル LLM 評価オーケストレーター](../epics/local-llm-evaluation-orchestrator.md)
- US-001: suite を検証する。
- US-002: 評価予定を dry-run で確認する。
- US-005: 実行結果の summary を残す。
- US-006: 外部依存なしに単体テストする。
- US-007: 日本語データを壊さない。

## 概要

`local-llm-eval` CLI は `validate` と `run` を提供する。`run` は `EvaluationPlan` の各 job について runner adapter でコマンドを生成し、dry-run では実行を省略し、通常実行では差し替え可能な command runner で外部コマンドを呼び出す。

## フィールド / パラメーター

### CLI

- `validate <suite>`: suite を検証する。
- `run <suite>`: suite を実行する。
- `run <suite> --dry-run`: 外部コマンドを実行せずに予定を記録する。
- `run <suite> --runs-dir <path>`: run 出力先の基準ディレクトリを指定する。

### summary.json

- `suite_id`: 実行対象 suite id。
- `run_dir`: run ディレクトリ。
- `dry_run`: dry-run かどうか。
- `jobs`: job ごとの結果リスト。
- `jobs[].model_id`: model id。
- `jobs[].benchmark_id`: benchmark id。
- `jobs[].runner`: runner 名。
- `jobs[].status`: `skipped`、`success`、`failed` のいずれか。
- `jobs[].exit_code`: dry-run では null、通常実行では終了コード。
- `jobs[].command`: runner adapter が生成したコマンド配列。
- `jobs[].raw_output_path`: raw 出力先。

## 振る舞い

- run ディレクトリは `<runs-dir>/<YYYY-MM-DDTHHMMSS>-<suite.id>` とする。
- 実行計画は `run.yaml.json` に保存する。
- summary は `summary.json` に保存する。
- JSON は UTF-8、インデント 2、`ensure_ascii=False` で書き出す。
- dry-run の job status は `skipped`、exit code は null とする。
- 通常実行では外部コマンドの終了コードが 0 の場合 `success`、それ以外は `failed` とする。
- 個別ジョブが失敗しても、後続ジョブの実行を継続する。
- `ConfigError` は CLI で捕捉し、標準エラーに `configuration error: ...` を出して終了コード 2 を返す。

## 検証

- `tests/test_executor.py::test_execute_plan_dry_run_writes_summary_without_running` で dry-run summary を確認する。
- `tests/test_executor.py::test_execute_plan_continues_after_failed_command` で失敗 exit code が summary に残ることを確認する。
- `tests/test_cli.py::test_validate_command_returns_success` で `validate` の成功終了を確認する。
- `tests/test_cli.py::test_run_dry_run_returns_success` で `run --dry-run` の成功終了と run 出力作成を確認する。

## エラー

- 設定解決時の `ConfigError` は CLI 終了コード 2 になる。
- 外部コマンドの非 0 終了はプロセス全体の即時失敗にはせず、job status と exit code として summary に残す。

## 例

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval validate config/suites/baseline.yaml
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval run config/suites/baseline.yaml --dry-run
```

## 未解決事項

- 通常実行時に一部 job が失敗した場合の CLI 全体の終了コード方針は、現行実装では summary 記録中心であり明確化余地がある。
