# runner adapter とコマンド生成

## 元になった要求

- Epic: [ローカル LLM 評価オーケストレーター](../epics/local-llm-evaluation-orchestrator.md)
- US-002: 評価予定を dry-run で確認する。
- US-004: 評価フレームワークごとのコマンドを隠蔽する。
- US-006: 外部依存なしに単体テストする。

## 概要

`EvaluationJob` と output directory から、runner 別の外部コマンドを生成する。評価フレームワーク本体の推論や採点は実行せず、adapter はコマンド引数と必要な補助ファイルの生成だけを担当する。

## フィールド / パラメーター

- `job`: model と benchmark を含む評価ジョブ。
- `output_dir`: runner の raw 出力先ディレクトリ。
- `job.benchmark.runner`: コマンド生成先を選ぶ runner 名。

## 振る舞い

### lm-evaluation-harness

- コマンド名は `lm-eval`。
- model は `local-chat-completions` を使う。
- `base_url`、`model`、`tokenized_requests=False` を `--model_args` に含める。
- benchmark の `task` を `--tasks` に渡す。
- raw 出力先を `--output_path` に渡す。
- `--log_samples` と `--apply_chat_template` を付与する。
- `runner_params.num_fewshot` がある場合は `--num_fewshot` に渡す。
- `generation.max_tokens` は `max_gen_toks`、`generation.temperature` は `temperature` として `--gen_kwargs` に渡す。

### OpenCompass

- コマンド名は `opencompass`。
- `output_dir/opencompass_config.py` を UTF-8 で生成する。
- 生成 config の model には `OpenAI` adapter、`openai_api_base`、`path`、`key`、`max_out_len`、`temperature` を設定する。
- API key は `api_key_env` があればその環境変数、なければ `LOCAL_LLM_API_KEY` から取得する式を生成する。
- dataset には benchmark の `dataset`、`dataset_format`、`evaluator` を反映する。
- `--config` と `--work-dir` で生成 config と出力先を渡す。

## 検証

- `tests/test_runners.py::test_build_lm_eval_command_for_openai_compatible_chat_api` で lm-evaluation-harness の引数を確認する。
- `tests/test_runners.py::test_build_opencompass_command_creates_generated_config_path` で OpenCompass コマンドと生成 config の存在を確認する。
- 単体テストでは `lm-eval` と `opencompass` を実行しない。

## エラー

- runner 名の検証は benchmark YAML 読み込み時に行う。
- executor が未知 runner の job を受け取った場合は `ValueError("Unsupported runner: ...")` を送出する。

## 例

```text
lm-eval --model local-chat-completions --tasks mmlu --model_args base_url=http://localhost:11434/v1,model=llama3.1:8b,tokenized_requests=False --output_path runs/.../raw/ollama-llama3/mmlu --log_samples --apply_chat_template --num_fewshot 5 --gen_kwargs max_gen_toks=512,temperature=0
```

## 未解決事項

- OpenCompass の dataset 設定は現行実装に合わせた最小生成であり、複雑な dataset 定義の全パターンを扱う仕様ではない。
