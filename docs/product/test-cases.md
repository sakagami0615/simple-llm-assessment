# テストケース

## テストケース一覧

| TC-ID | テストケース名 | 対象仕様 | 関数名 |
| --- | --- | --- | --- |
| TC-001 | model YAML を読み込む | [設定モデルと YAML 検証](specs/configuration-models.md) | `tests/test_config.py::test_load_model_config` |
| TC-002 | lm-evaluation-harness benchmark YAML を読み込む | [設定モデルと YAML 検証](specs/configuration-models.md) | `tests/test_config.py::test_load_lm_eval_benchmark_config` |
| TC-003 | OpenCompass benchmark YAML を読み込む | [設定モデルと YAML 検証](specs/configuration-models.md) | `tests/test_config.py::test_load_opencompass_benchmark_config` |
| TC-004 | suite YAML を読み込む | [設定モデルと YAML 検証](specs/configuration-models.md) | `tests/test_config.py::test_load_suite_config` |
| TC-005 | 必須項目不足を拒否する | [設定モデルと YAML 検証](specs/configuration-models.md) | `tests/test_config.py::test_missing_required_field_raises_config_error` |
| TC-006 | 未知 runner を拒否する | [設定モデルと YAML 検証](specs/configuration-models.md) | `tests/test_config.py::test_unknown_runner_raises_config_error` |
| TC-007 | suite を job に展開する | [suite 計画とジョブ展開](specs/suite-planning.md) | `tests/test_planner.py::test_plan_suite_expands_model_by_benchmark_jobs` |
| TC-008 | suite の参照欠落を拒否する | [suite 計画とジョブ展開](specs/suite-planning.md) | `tests/test_planner.py::test_plan_suite_rejects_missing_referenced_file` |
| TC-009 | lm-evaluation-harness コマンドを生成する | [runner adapter とコマンド生成](specs/runner-adapters.md) | `tests/test_runners.py::test_build_lm_eval_command_for_openai_compatible_chat_api` |
| TC-010 | OpenCompass コマンドと生成 config を作る | [runner adapter とコマンド生成](specs/runner-adapters.md) | `tests/test_runners.py::test_build_opencompass_command_creates_generated_config_path` |
| TC-011 | dry-run summary を保存する | [CLI 実行と結果保存](specs/cli-execution-results.md) | `tests/test_executor.py::test_execute_plan_dry_run_writes_summary_without_running` |
| TC-012 | 外部コマンド失敗を summary に残す | [CLI 実行と結果保存](specs/cli-execution-results.md) | `tests/test_executor.py::test_execute_plan_continues_after_failed_command` |
| TC-013 | validate CLI が成功する | [CLI 実行と結果保存](specs/cli-execution-results.md) | `tests/test_cli.py::test_validate_command_returns_success` |
| TC-014 | run dry-run CLI が成功する | [CLI 実行と結果保存](specs/cli-execution-results.md) | `tests/test_cli.py::test_run_dry_run_returns_success` |
| TC-015 | プロジェクト構造を守る | [システムダイアグラム](diagram.md) | `tests/test_project_structure.py` |

## TC-001: model YAML を読み込む

### 対象仕様

[設定モデルと YAML 検証](specs/configuration-models.md)

### テスト名 / 関数名

`tests/test_config.py::test_load_model_config`

### 入力パラメーター

`id`、`provider`、`base_url`、`model`、`api_key_env`、`generation` を持つ model YAML。

### 実行する内容

`load_model_config()` で YAML を読み込む。

### 期待結果

`ModelConfig` に変換され、`generation` と読み込み元 `path` を保持する。

### 備考

UTF-8 でテストファイルを作成する。

## TC-002: lm-evaluation-harness benchmark YAML を読み込む

### 対象仕様

[設定モデルと YAML 検証](specs/configuration-models.md)

### テスト名 / 関数名

`tests/test_config.py::test_load_lm_eval_benchmark_config`

### 入力パラメーター

`runner: lm-evaluation-harness`、`task`、`runner_params.num_fewshot`、`metrics` を持つ benchmark YAML。

### 実行する内容

`load_benchmark_config()` で YAML を読み込む。

### 期待結果

`BenchmarkConfig` に変換され、runner 名、task、runner params、metrics が保持される。

### 備考

runner 名は正式名称である。

## TC-003: OpenCompass benchmark YAML を読み込む

### 対象仕様

[設定モデルと YAML 検証](specs/configuration-models.md)

### テスト名 / 関数名

`tests/test_config.py::test_load_opencompass_benchmark_config`

### 入力パラメーター

`runner: OpenCompass`、`dataset`、`dataset_format`、`evaluator`、`metrics` を持つ benchmark YAML。

### 実行する内容

`load_benchmark_config()` で YAML を読み込む。

### 期待結果

runner、dataset、metrics が `BenchmarkConfig` に保持される。

### 備考

日本語を含む dataset は別ファイルとして UTF-8 で扱う。

## TC-004: suite YAML を読み込む

### 対象仕様

[設定モデルと YAML 検証](specs/configuration-models.md)

### テスト名 / 関数名

`tests/test_config.py::test_load_suite_config`

### 入力パラメーター

`id`、`models`、`benchmarks` を持つ suite YAML。

### 実行する内容

`load_suite_config()` で YAML を読み込む。

### 期待結果

`SuiteConfig` に変換され、参照リストと読み込み元 `path` が保持される。

### 備考

`models` と `benchmarks` は文字列リストでなければならない。

## TC-005: 必須項目不足を拒否する

### 対象仕様

[設定モデルと YAML 検証](specs/configuration-models.md)

### テスト名 / 関数名

`tests/test_config.py::test_missing_required_field_raises_config_error`

### 入力パラメーター

`provider` がない model YAML。

### 実行する内容

`load_model_config()` で YAML を読み込む。

### 期待結果

`ConfigError` が送出され、エラーメッセージに `provider` が含まれる。

### 備考

実行前に設定不備を止めるためのテスト。

## TC-006: 未知 runner を拒否する

### 対象仕様

[設定モデルと YAML 検証](specs/configuration-models.md)

### テスト名 / 関数名

`tests/test_config.py::test_unknown_runner_raises_config_error`

### 入力パラメーター

`runner: unknown` を持つ benchmark YAML。

### 実行する内容

`load_benchmark_config()` で YAML を読み込む。

### 期待結果

`ConfigError` が送出され、エラーメッセージに runner が含まれる。

### 備考

許可 runner は `lm-evaluation-harness` と `OpenCompass`。

## TC-007: suite を job に展開する

### 対象仕様

[suite 計画とジョブ展開](specs/suite-planning.md)

### テスト名 / 関数名

`tests/test_planner.py::test_plan_suite_expands_model_by_benchmark_jobs`

### 入力パラメーター

1 model、1 benchmark を参照する suite YAML。

### 実行する内容

`plan_suite()` で suite を解決する。

### 期待結果

`EvaluationJob` が 1 件生成され、`output_name` が `<model.id>/<benchmark.id>` になる。

### 備考

複数 model / benchmark の場合は直積に拡張される。

## TC-008: suite の参照欠落を拒否する

### 対象仕様

[suite 計画とジョブ展開](specs/suite-planning.md)

### テスト名 / 関数名

`tests/test_planner.py::test_plan_suite_rejects_missing_referenced_file`

### 入力パラメーター

存在しない model YAML を参照する suite YAML。

### 実行する内容

`plan_suite()` で suite を解決する。

### 期待結果

`ConfigError("Referenced file does not exist: ...")` が送出される。

### 備考

参照は `config/` 基準で解決する。

## TC-009: lm-evaluation-harness コマンドを生成する

### 対象仕様

[runner adapter とコマンド生成](specs/runner-adapters.md)

### テスト名 / 関数名

`tests/test_runners.py::test_build_lm_eval_command_for_openai_compatible_chat_api`

### 入力パラメーター

OpenAI 互換 model と `runner: lm-evaluation-harness` benchmark の `EvaluationJob`。

### 実行する内容

`build_lm_eval_command()` で command list を生成する。

### 期待結果

`lm-eval`、`local-chat-completions`、task、`base_url`、model、`--output_path`、`--apply_chat_template`、`--num_fewshot` が含まれる。

### 備考

外部コマンドは実行しない。

## TC-010: OpenCompass コマンドと生成 config を作る

### 対象仕様

[runner adapter とコマンド生成](specs/runner-adapters.md)

### テスト名 / 関数名

`tests/test_runners.py::test_build_opencompass_command_creates_generated_config_path`

### 入力パラメーター

OpenAI 互換 model と `runner: OpenCompass` benchmark の `EvaluationJob`。

### 実行する内容

`build_opencompass_command()` で command list を生成する。

### 期待結果

`opencompass`、`--config`、`opencompass_config.py`、`--work-dir` が含まれ、config ファイルが作成される。

### 備考

生成 config は UTF-8 で書き出す。

## TC-011: dry-run summary を保存する

### 対象仕様

[CLI 実行と結果保存](specs/cli-execution-results.md)

### テスト名 / 関数名

`tests/test_executor.py::test_execute_plan_dry_run_writes_summary_without_running`

### 入力パラメーター

1 job を持つ `EvaluationPlan`、`dry_run=True`。

### 実行する内容

`execute_plan()` を実行する。

### 期待結果

run directory と `summary.json` が作成され、job status が `skipped` になり、command に `lm-eval` が含まれる。

### 備考

外部コマンドは実行しない。

## TC-012: 外部コマンド失敗を summary に残す

### 対象仕様

[CLI 実行と結果保存](specs/cli-execution-results.md)

### テスト名 / 関数名

`tests/test_executor.py::test_execute_plan_continues_after_failed_command`

### 入力パラメーター

終了コード 7 を返す `command_runner`。

### 実行する内容

`execute_plan()` を `dry_run=False` で実行する。

### 期待結果

`summary.json` に `status: failed` と `exit_code: 7` が記録される。

### 備考

失敗ジョブがあっても summary を保存する。

## TC-013: validate CLI が成功する

### 対象仕様

[CLI 実行と結果保存](specs/cli-execution-results.md)

### テスト名 / 関数名

`tests/test_cli.py::test_validate_command_returns_success`

### 入力パラメーター

有効な model、benchmark、suite YAML。

### 実行する内容

`main(["validate", suite])` を実行する。

### 期待結果

終了コード 0 を返す。

### 備考

実評価は行わない。

## TC-014: run dry-run CLI が成功する

### 対象仕様

[CLI 実行と結果保存](specs/cli-execution-results.md)

### テスト名 / 関数名

`tests/test_cli.py::test_run_dry_run_returns_success`

### 入力パラメーター

有効な model、benchmark、suite YAML、`--dry-run`、`--runs-dir`。

### 実行する内容

`main(["run", suite, "--dry-run", "--runs-dir", runs_dir])` を実行する。

### 期待結果

終了コード 0 を返し、run 出力が作成される。

### 備考

外部評価フレームワークは実行しない。

## TC-015: プロジェクト構造を守る

### 対象仕様

[システムダイアグラム](diagram.md)

### テスト名 / 関数名

`tests/test_project_structure.py`

### 入力パラメーター

現在のリポジトリファイル構成。

### 実行する内容

パッケージ配置、旧パッケージ非存在、生成キャッシュ非混入、公開 API docstring を確認する。

### 期待結果

`src/local_llm_eval/` が存在し、旧 `app/llm_qa_app` と `app/llm_eval` がなく、公開 API に docstring がある。

### 備考

生成物を成果物に混ぜない方針を守る。
