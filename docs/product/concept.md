# コンセプト

## 目的

`local-llm-eval` は、ローカルで起動済みの LLM サーバを対象に、定番の評価フレームワークを一括実行するための薄い CLI オーケストレーターである。

評価そのもの、モデル推論、採点ロジックは、可能な限り lm-evaluation-harness と OpenCompass に委譲する。プロジェクトは、設定の検証、suite から評価ジョブへの展開、外部コマンド生成、実行結果の保存を担当する。

## 対象ユーザー

- ローカル LLM を継続的に比較したい開発者。
- Ollama、vLLM、LM Studio、llama.cpp server などの OpenAI 互換 API サーバを自分で管理している評価担当者。
- lm-evaluation-harness と OpenCompass を直接扱う前に、プロジェクト内の YAML で評価対象を整理したい利用者。

## 解決したい課題

- モデル、ベンチマーク、suite の指定が散らばると、同じ評価を再現しにくい。
- 評価フレームワークごとにコマンド形式が異なり、ローカル LLM サーバ向けの引数を毎回手で組み立てる必要がある。
- ローカル LLM の実評価は重いため、実行前に設定解決と生成コマンドだけを確認したい。
- 日本語を含む自作 QA データセットや JSON 出力を壊さず扱いたい。

## ゴール

- 1 model = 1 YAML、1 benchmark = 1 YAML、suite YAML がそれらを参照する構成を保つ。
- `local-llm-eval validate <suite>` で設定と参照を検証できる。
- `local-llm-eval run <suite> --dry-run` で外部評価を実行せず、予定コマンドと summary を確認できる。
- `local-llm-eval run <suite>` で suite 内の model x benchmark ジョブを順に実行し、結果メタデータを `runs/` に保存できる。
- runner 名は正式名称の `lm-evaluation-harness` と `OpenCompass` に限定する。

## 非ゴール

- OpenAI などのホステッドモデルプロバイダーを使うこと。
- ローカル LLM サーバの起動、停止、ヘルスチェックを管理すること。
- lm-evaluation-harness や OpenCompass の評価ロジックを再実装すること。
- 重い外部評価フレームワークを通常の単体テストで実行すること。
- `runs/`、`__pycache__/`、`.pytest_cache/` などの生成物を成果物として管理すること。

## 成功条件

- 非 ignored の設定、実装、テスト、既存ドキュメントから、AIDD の正本ドキュメントが `docs/product/` に整理されている。
- README にある基本コマンドが正本ドキュメント上の仕様と一致している。
- 設定エラーは `ConfigError` として実行前に扱われる。
- dry-run では外部コマンドを呼ばずに `summary.json` が作成される。
- 日本語を含むデータセットと JSON 出力が UTF-8 と `ensure_ascii=False` の方針で扱われる。
