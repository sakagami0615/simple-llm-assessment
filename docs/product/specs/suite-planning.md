# suite 計画とジョブ展開

## 元になった要求

- Epic: [ローカル LLM 評価オーケストレーター](../epics/local-llm-evaluation-orchestrator.md)
- US-001: suite を検証する。
- US-003: 複数ジョブを suite から展開して実行する。

## 概要

suite YAML を起点に model YAML と benchmark YAML の参照を解決し、全組み合わせの `EvaluationJob` を含む `EvaluationPlan` を作る。

## フィールド / パラメーター

### EvaluationJob

- `model`: 解決済み `ModelConfig`。
- `benchmark`: 解決済み `BenchmarkConfig`。
- `output_name`: raw 出力用の相対パス要素。形式は `<model.id>/<benchmark.id>`。

### EvaluationPlan

- `suite`: 解決済み `SuiteConfig`。
- `models`: 解決済み model 設定リスト。
- `benchmarks`: 解決済み benchmark 設定リスト。
- `jobs`: 展開済み評価ジョブリスト。

## 振る舞い

- suite ファイルは通常 `config/suites/<suite>.yaml` に置く。
- suite 内の参照は `config/` を基準に解決する。
- `models` と `benchmarks` の直積を評価ジョブとして展開する。
- 出力名は model id と benchmark id の組み合わせで決定する。

## 検証

- `tests/test_planner.py::test_plan_suite_expands_model_by_benchmark_jobs` で suite からジョブへ展開できることを確認する。
- `tests/test_planner.py::test_plan_suite_rejects_missing_referenced_file` で参照ファイル欠落時に `ConfigError` になることを確認する。

## エラー

- suite から参照された model または benchmark ファイルが存在しない場合は `ConfigError("Referenced file does not exist: ...")` を送出する。
- 参照先 YAML の検証エラーは、設定モデルの `ConfigError` として呼び出し元へ伝播する。

## 例

```yaml
id: baseline
models:
  - models/ollama-llama3.yaml
benchmarks:
  - benchmarks/mmlu.yaml
```

この suite は、`ollama-llama3` と `mmlu` の 1 ジョブに展開される。

## 未解決事項

- 大量ジョブの並列実行、フィルタリング、再実行指定は現行仕様に含めない。
