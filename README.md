# local-llm-eval

ローカル LLM サーバを対象に、lm-evaluation-harness と OpenCompass の評価を一括実行するための薄いオーケストレーターです。

## セットアップ

```bash
poetry install --with eval
```

依存関係の補足は [docs/APPENDIX.md](docs/APPENDIX.md) を参照してください。

## 前提

Ollama、vLLM、LM Studio、llama.cpp server などのローカル LLM サーバは事前に起動しておきます。このツールはサーバ起動を管理しません。

モデルサーバは OpenAI 互換 API を提供している前提です。OpenAI 社のホステッド API は使わず、`base_url` は `http://localhost:.../v1` のようなローカルエンドポイントを指定します。

## 実行

設定の検証:

```bash
poetry run local-llm-eval validate config/suites/baseline.yaml
```

実行予定コマンドの確認:

```bash
poetry run local-llm-eval run config/suites/baseline.yaml --dry-run
```

評価の実行:

```bash
poetry run local-llm-eval run config/suites/baseline.yaml
```

## 構成

```text
.
├── config/
│   ├── models/
│   │   ├── ollama-llama3.yaml
│   │   └── vllm-qwen2-7b.yaml
│   ├── benchmarks/
│   │   ├── mmlu.yaml
│   │   └── my_internal_qa.yaml
│   └── suites/
│       └── baseline.yaml
├── datasets/
│   └── my_internal_qa.json
├── src/
│   └── local_llm_eval/
│       ├── cli.py
│       ├── config.py
│       ├── planner.py
│       ├── executor.py
│       ├── results.py
│       └── runners/
│           ├── lm_evaluation_harness.py
│           └── opencompass.py
├── tests/
├── docs/
└── runs/
```

- `config/models/`: 1モデル接続 = 1 YAML
- `config/benchmarks/`: 1ベンチマーク = 1 YAML
- `config/suites/`: 実行する model と benchmark の束
- `datasets/`: 自作データセット
- `runs/`: 実行結果
- `src/local_llm_eval/`: CLI とオーケストレーション実装

## モデル定義

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

## ベンチマーク定義

lm-evaluation-harness:

```yaml
id: mmlu
runner: lm-evaluation-harness
task: mmlu
runner_params:
  num_fewshot: 5
metrics:
  - acc
```

OpenCompass:

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

## スイート定義

```yaml
id: baseline
models:
  - models/ollama-llama3.yaml
benchmarks:
  - benchmarks/mmlu.yaml
```

## テスト

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q
```

テストコードの内容は [docs/TESTING.md](docs/TESTING.md) を参照してください。
