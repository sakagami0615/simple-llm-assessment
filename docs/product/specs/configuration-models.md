# 設定モデルと YAML 検証

## 元になった要求

- Epic: [ローカル LLM 評価オーケストレーター](../epics/local-llm-evaluation-orchestrator.md)
- US-001: suite を検証する。
- US-004: 評価フレームワークごとのコマンドを隠蔽する。
- US-007: 日本語データを壊さない。

## 概要

model、benchmark、suite の YAML を読み込み、検証済み dataclass として扱う。設定ファイルの構造不備、必須項目不足、未対応 provider、未対応 runner は `ConfigError` で表現する。

## フィールド / パラメーター

### ModelConfig

- `id`: リポジトリ内のモデル識別子。
- `provider`: 現在は `openai_compatible` のみ。
- `base_url`: ローカル LLM サーバの OpenAI 互換 API ベース URL。
- `model`: ローカルサーバへ渡すモデル名。
- `api_key_env`: API キーを格納する任意の環境変数名。
- `generation`: `temperature`、`max_tokens` などの生成パラメーター。
- `path`: 読み込み元 YAML パス。

### BenchmarkConfig

- `id`: ベンチマーク識別子。
- `runner`: `lm-evaluation-harness` または `OpenCompass`。
- `task`: lm-evaluation-harness などが使うタスク名。
- `dataset`: OpenCompass などが使うデータセットパス。
- `dataset_format`: データセット形式。
- `evaluator`: evaluator 名。
- `runner_params`: runner 固有パラメーター。
- `metrics`: 期待する metric 名。
- `path`: 読み込み元 YAML パス。

### SuiteConfig

- `id`: suite 識別子。
- `models`: model YAML への参照リスト。
- `benchmarks`: benchmark YAML への参照リスト。
- `path`: 読み込み元 YAML パス。

## 振る舞い

- YAML は UTF-8 として読み込む。
- YAML のトップレベルは mapping でなければならない。
- model YAML の `generation` は省略可能で、省略時は空の mapping とする。
- benchmark YAML の `metrics` は省略可能で、省略時は空の list とする。
- benchmark YAML の `runner_params` は省略可能で、省略時は空の mapping とする。
- suite YAML の `models` と `benchmarks` は文字列リストでなければならない。
- runner 名は正式名称で検証する。

## 検証

- `tests/test_config.py` で model、benchmark、suite の正常系を確認する。
- 必須項目不足は `ConfigError` を送出する。
- 未知 runner は `ConfigError` を送出する。
- `tests/test_cli.py` で `validate` が設定解決に成功することを確認する。

## エラー

- ファイルが存在しない場合: `ConfigError("Config file does not exist: ...")`
- YAML が mapping でない場合: `ConfigError("Config file must contain a mapping: ...")`
- 必須項目がない場合: `ConfigError("Missing required field ...")`
- provider が `openai_compatible` 以外の場合: `ConfigError("Unsupported provider ...")`
- runner が `lm-evaluation-harness` / `OpenCompass` 以外の場合: `ConfigError("Unsupported runner ...")`

## 例

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

## 未解決事項

- `metrics` の意味は benchmark ごとに異なるため、現状は型検証に留める。
