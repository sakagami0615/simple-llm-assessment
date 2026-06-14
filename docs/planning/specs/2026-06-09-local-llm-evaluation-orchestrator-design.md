# ローカル LLM 評価オーケストレーター設計

## 目的

ローカルモデルサーバに対してベンチマークスイートを実行できる、ローカル LLM 評価環境を構築する。評価資産は、モデル、ベンチマーク、スイート、データセット、実行結果を中心に整理する。

このリポジトリでは、以下を扱えるようにする。

- Ollama、llama.cpp server、vLLM、LM Studio、および OpenAI 互換 API を提供する任意のローカル LLM サーバ。
- lm-evaluation-harness や OpenCompass などの既存ベンチマークフレームワーク。
- それらのフレームワーク向けに変換、または設定されたユーザー独自データセット。
- 複数のモデル定義とベンチマーク定義を参照するスイートのワンコマンド実行。

## 対象外

- ローカルモデルサーバの起動や管理。Ollama、vLLM、LM Studio、llama.cpp server などは、評価実行前にユーザーが起動しておく。
- モデル推論処理の直接実装。
- 既存フレームワークの metric や evaluator を使える場合の、ベンチマーク採点処理の直接実装。
- OpenAI などのホステッドモデルプロバイダーの利用。
- 以前の OpenAI / DeepEval 実装の維持。

## 設計方針

スイート中心のオーケストレーターとして設計する。このリポジトリは単一の CLI エントリーポイントを提供し、suite YAML を読み込み、参照されている model YAML と benchmark YAML を解決し、各ジョブを適切な評価フレームワークへ振り分け、結果を1つの run ディレクトリに保存する。

lm-evaluation-harness と OpenCompass は、評価資産を分断する単位ではなく、実行バックエンドとして扱う。raw 出力の都合で必要な場合を除き、datasets、suites、runs をフレームワーク別に分割しない。

## ディレクトリ構成

```text
models/
  ollama-llama3.yaml
  vllm-qwen2-7b.yaml
  lmstudio-local.yaml

benchmarks/
  mmlu.yaml
  arc_challenge.yaml
  my_internal_qa.yaml

suites/
  baseline.yaml
  japanese_eval.yaml
  coding_eval.yaml

datasets/
  my_internal_qa.json
  my_mcq.jsonl

runs/
  2026-06-09T230000-baseline/
    run.yaml
    summary.json
    logs/
      local-llm-eval.log
    raw/
      ollama-llama3/
        mmlu/
      vllm-qwen2-7b/
        mmlu/

src/local_llm_eval/
  cli.py
  config.py
  planner.py
  runners/
    lm_evaluation_harness.py
    opencompass.py
```

## モデル定義

モデル接続ごとに1つの YAML ファイルを用意する。

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

各フィールドの意味:

- `id`: このリポジトリ内で使うモデル識別子。
- `provider`: 初期値は `openai_compatible`。
- `base_url`: ローカルサーバ API のベース URL。
- `model`: ローカルサーバへ渡すモデル名。
- `api_key_env`: API キー、またはダミーキーを必要とするローカルサーバ向けの任意環境変数。
- `generation`: 共通の生成設定。

## ベンチマーク定義

ベンチマークごとに1つの YAML ファイルを用意する。

lm-evaluation-harness の例:

```yaml
id: mmlu
runner: lm-evaluation-harness
task: mmlu
runner_params:
  num_fewshot: 5
metrics:
  - acc
```

OpenCompass の例:

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

`runner` にはツールの正式名称を使う。

- `lm-evaluation-harness`
- `OpenCompass`

`runner_params` には、フレームワーク固有のパラメータを記載する。たとえば `num_fewshot` は、few-shot 評価に対応しているタスクで、評価プロンプトに含める例題数を制御する。

## スイート定義

スイートは model ファイルと benchmark ファイルを参照する。

```yaml
id: baseline
models:
  - models/ollama-llama3.yaml
  - models/vllm-qwen2-7b.yaml
benchmarks:
  - benchmarks/mmlu.yaml
  - benchmarks/arc_challenge.yaml
  - benchmarks/my_internal_qa.yaml
```

この構成により、巨大な単一ベンチマークファイルを避けつつ、複数ベンチマークを1つのコマンドで実行できる。

## CLI

主なエントリーポイント:

```bash
poetry run local-llm-eval run suites/baseline.yaml
```

検証:

```bash
poetry run local-llm-eval validate suites/baseline.yaml
```

dry-run:

```bash
poetry run local-llm-eval run suites/baseline.yaml --dry-run
```

`run` は外部評価フレームワークのコマンドを実行する。`--dry-run` は実行予定のコマンドを表示するだけで、実際には実行しない。`validate` は YAML 構造、参照、モデル ID、runner 名、必須フィールド、参照ファイルの存在を検証する。

## 実行フロー

1. suite YAML を読み込む。
2. model YAML ファイルを解決する。
3. benchmark YAML ファイルを解決する。
4. 実行前に、解決済みの定義をすべて検証する。
5. suite を model x benchmark のジョブへ展開する。
6. 各ジョブについて、`runner` に応じた runner adapter を選択する。
7. 評価フレームワークのコマンドを生成する。
8. `--dry-run` が指定されていなければコマンドを実行する。
9. フレームワークの raw 出力を `runs/<run-id>/raw/` に保存する。
10. `run.yaml`、ログ、`summary.json` を書き出す。

## 結果保存

各実行ごとに、`runs/` 配下へ新しいディレクトリを作成する。

`run.yaml` には、その実行で使用した解決済みの suite、model、benchmark 定義を保存する。

`summary.json` には以下を保存する。

- run ID と suite ID。
- 開始・終了時刻。
- model ID。
- benchmark ID。
- runner 名。
- ステータス: `success`、`failed`、`skipped`。
- 終了コード。
- raw 出力のパス。
- 取得できた場合の抽出済み metrics。

metric 抽出が不完全な場合でも、フレームワークの raw 出力は保持する。

## エラー処理

検証エラーは、ベンチマーク実行前に処理を停止する。例:

- suite YAML をパースできない。
- 参照されている model または benchmark ファイルが存在しない。
- 必須フィールドが不足している。
- runner 名が不明。
- 外部コマンドが利用できない。

実行時エラーはジョブ単位で分離する。1つのベンチマークが失敗しても、残りの model x benchmark ジョブは継続する。最終 summary に各失敗を記録する。

## 依存関係管理

Poetry を使う。評価フレームワークは eval dependency group でインストールできるようにする。

```bash
poetry install --with eval
```

eval group には、lm-evaluation-harness、OpenCompass、および必要な dataset / configuration 補助ライブラリを含める。

## 以前の実装の削除

実装時には、既存の OpenAI / DeepEval 前提コードを削除してよい。

- `app/llm_qa_app/`
- `app/llm_eval/`
- DeepEval / OpenAI 固有のテスト。
- 新しい流れに合わない場合の `scripts/convert_hf_dataset.py`。
- 以前の実装に紐づくサンプル評価データ。
- 以前の OpenAI / DeepEval ドキュメント。

`README.md`、`ARCHITECTURE.md`、`pyproject.toml` は、ローカル LLM 評価オーケストレーター向けに全面更新する。

## テスト方針

初期テストでは、重い外部評価は実行しない。

以下を対象にする。

- YAML 読み込みと検証。
- suite から model x benchmark ジョブへ展開できること。
- lm-evaluation-harness 向けコマンド生成。
- OpenCompass 向けコマンド生成。
- `--dry-run` の挙動。
- コマンド失敗時の handling と summary 出力。
- 古いコード削除後のプロジェクト構成。

コマンド実行テストでは、fake runner コマンドまたは mock を使う。

## 実装時に決めること

- lm-evaluation-harness で OpenAI 互換ローカルサーバを使う際の正確なコマンドライン対応。
- OpenCompass で OpenAI 互換ローカルサーバを使う際の生成 config 形式。
- 各フレームワークの raw 出力から metric を抽出する詳細。
- 初期実装で、自作データセット変換補助を ChatML、lm-evaluation-harness YAML task、または両方のどれに寄せるか。
