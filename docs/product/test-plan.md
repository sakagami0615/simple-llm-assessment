# テスト方針

## 戦略

単体テストでは、ローカル LLM サーバ、lm-evaluation-harness、OpenCompass を実行しない。代わりに、設定検証、suite 展開、runner コマンド生成、executor の summary 保存、CLI の成功終了を小さく確認する。

外部コマンド実行は `CommandRunner` を差し替えて検証する。実評価の動作確認は、別途ローカル LLM サーバと eval dependency を準備した環境で行う。

## テストレベル

- Unit: `config.py`、`planner.py`、runner adapter、`results.py` 相当の純粋処理を検証する。
- Component: `executor.py` が run ディレクトリ、`run.yaml.json`、`summary.json` を作ることを検証する。
- CLI: `main()` に引数を渡し、`validate` と `run --dry-run` の終了コードを検証する。
- Structure: パッケージ配置、旧パッケージの非存在、生成キャッシュの非混入、公開 API docstring を検証する。

## 検証対象

- model YAML の読み込みと provider 検証。
- benchmark YAML の読み込みと runner 検証。
- suite YAML の読み込みと参照解決。
- model x benchmark の job 展開。
- lm-evaluation-harness コマンド生成。
- OpenCompass コマンド生成と一時 config 生成。
- dry-run 時に外部コマンドを実行しないこと。
- 外部コマンド失敗時に summary へ `failed` と exit code を残すこと。
- CLI の `validate` と `run --dry-run`。
- UTF-8 ファイル読み書きと JSON の `ensure_ascii=False` 方針。

## 外部依存の扱い

- lm-evaluation-harness と OpenCompass の実評価は通常テストで実行しない。
- ローカル LLM サーバへの通信は行わない。
- OpenCompass の依存である `torch` などが Python 3.14 で未対応の場合があるため、CLI 本体の検証と実評価環境を分ける。
- pytest plugin の自動読み込み副作用を避けるため、検証コマンドでは `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` を使う。

## 非ゴール

- 実モデルの品質、精度、採点妥当性を単体テストで保証すること。
- runner フレームワーク内部の挙動をテストすること。
- 生成された `runs/` を成果物として検証対象に含め続けること。

## 推奨検証コマンド

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval validate config/suites/baseline.yaml
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run local-llm-eval run config/suites/baseline.yaml --dry-run
```
