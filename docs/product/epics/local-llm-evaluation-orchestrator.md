# ローカル LLM 評価オーケストレーター

## 概要

ローカル LLM サーバを対象にした評価バッチを YAML で定義し、lm-evaluation-harness と OpenCompass に委譲して実行する CLI を提供する。プロジェクトの責務は、設定検証、参照解決、評価ジョブ展開、runner 別コマンド生成、実行結果メタデータ保存である。

## 関連ユーザーストーリー

- US-001: suite を検証する。
- US-002: 評価予定を dry-run で確認する。
- US-003: 複数ジョブを suite から展開して実行する。
- US-004: 評価フレームワークごとのコマンドを隠蔽する。
- US-005: 実行結果の summary を残す。
- US-006: 外部依存なしに単体テストする。
- US-007: 日本語データを壊さない。

## 機能要求

- model、benchmark、suite の YAML を読み込み、dataclass に変換する。
- model YAML は `provider: openai_compatible` のみを受け付ける。
- benchmark YAML は runner 名として `lm-evaluation-harness` または `OpenCompass` のみを受け付ける。
- suite YAML は `models` と `benchmarks` の参照を持ち、参照先を `config/` 配下から解決する。
- suite 内の全 model と全 benchmark の直積を `EvaluationJob` に展開する。
- `validate` は評価を実行せず、設定解決に成功した場合に成功終了する。
- `run --dry-run` は外部コマンドを実行せず、summary と予定コマンドを保存する。
- `run` は各ジョブの外部コマンドを順に実行し、失敗ジョブがあっても残りのジョブを継続する。
- JSON 出力は UTF-8 で書き出し、必要がない限り日本語をエスケープしない。

## 非機能要求

- CLI 本体の開発、設定検証、dry-run は Python 3.14 で動作する。
- 実評価用の eval dependency は Python 3.14 で利用できない場合があるため、Python 3.13 以下の実評価環境を許容する。
- 単体テストでは lm-evaluation-harness、OpenCompass、ローカル LLM サーバを実行しない。
- 外部コマンド実行は差し替え可能な関数として注入できる。
- 公開 API には docstring を付与する。

## 設計制約

- Python パッケージは `src/local_llm_eval/` 配下に置く。
- 設定ファイルは YAML を基本にする。
- `runs/` は生成物であり、成果物として扱わない。
- 既存評価フレームワークに委譲できる推論・採点ロジックを本プロジェクトで再実装しない。
- OpenAI などのホステッドモデルプロバイダーは使わない。

## 派生する Specs

- [設定モデルと YAML 検証](../specs/configuration-models.md)
- [suite 計画とジョブ展開](../specs/suite-planning.md)
- [runner adapter とコマンド生成](../specs/runner-adapters.md)
- [CLI 実行と結果保存](../specs/cli-execution-results.md)

## 受け入れ条件

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q` が成功する。
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval validate config/suites/baseline.yaml` が成功する。
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval run config/suites/baseline.yaml --dry-run` が成功し、summary を保存する。
- runner 名の誤り、必須項目不足、参照ファイル欠落は `ConfigError` として扱われる。

## 対象外

- ローカル LLM サーバのプロセス管理。
- 実評価結果の統計分析や可視化。
- 評価フレームワークごとの詳細な採点実装。
- ホステッドモデル API への接続。

## 未解決事項

- OpenCompass 用の生成 config が、実際の OpenCompass バージョンごとの dataset 定義差分にどこまで対応するかは未確定。
- `metrics` は現状メタデータとして読み込まれるが、runner コマンド生成では直接使われていない。
