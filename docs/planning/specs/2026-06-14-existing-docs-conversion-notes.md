# 既存ドキュメント変換メモ

## 目的

既存の非 ignored ドキュメントと実装から、AIDD フローの正本ドキュメントを `docs/product/` に作成するための参照メモ。

## 対象にしたファイル

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING.md`
- `docs/APPENDIX.md`
- `AGENTS.md`
- `pyproject.toml`
- `config/models/*.yaml`
- `config/benchmarks/*.yaml`
- `config/suites/*.yaml`
- `datasets/my_internal_qa.json`
- `src/local_llm_eval/**/*.py`
- `tests/*.py`
- `.codex/skills/aidd-flow/SKILL.md`
- `.codex/skills/aidd-flow/assets/templates/*.md`

## 対象外にしたファイル

- `.codex/skills` 以外の ignored ファイル。
- `runs/`、`__pycache__/`、`.pytest_cache/` などの生成物。
- 非 ignored 一覧に出てこなかった `docs/superpowers/` 配下の作業用資料は、内容を読まず、AIDD フローの置き場所ルールに従って `docs/planning/` へ移動した。

## 抽出したプロダクト方針

- このプロジェクトは、ローカル LLM 評価用 CLI `local-llm-eval` を提供する。
- モデル接続は OpenAI 互換 API を提供するローカルサーバを前提にする。
- OpenAI などのホステッドモデルプロバイダーは使わない。
- ローカル LLM サーバの起動は管理しない。
- 推論と採点は lm-evaluation-harness / OpenCompass に委譲する。
- 設定は YAML を基本とし、1 model = 1 YAML、1 benchmark = 1 YAML、suite YAML がそれらを参照する。
- runner 名は `lm-evaluation-harness` と `OpenCompass` の正式名称を使う。

## 抽出した実装方針

- `src/local_llm_eval/config.py` が YAML 読み込みと検証を担う。
- `src/local_llm_eval/planner.py` が suite から model x benchmark の `EvaluationJob` を展開する。
- `src/local_llm_eval/executor.py` が run ディレクトリ、`run.yaml.json`、`summary.json` を作成する。
- `src/local_llm_eval/runners/` が runner 別コマンド生成を担う。
- `src/local_llm_eval/results.py` が UTF-8 JSON 書き出しを担う。
- 外部コマンド実行は `CommandRunner` で差し替え可能にする。

## 正本への反映先

- プロダクトの目的、対象ユーザー、ゴール、非ゴール: `docs/product/concept.md`
- ユーザー価値と操作の流れ: `docs/product/user-stories.md`
- 開発単位としての要求: `docs/product/epics/local-llm-evaluation-orchestrator.md`
- 設定仕様: `docs/product/specs/configuration-models.md`
- suite 展開仕様: `docs/product/specs/suite-planning.md`
- runner adapter 仕様: `docs/product/specs/runner-adapters.md`
- CLI と結果保存仕様: `docs/product/specs/cli-execution-results.md`
- 中核概念: `docs/product/domain-model.md`
- 実装構造と図: `docs/product/diagram.md`
- 検証方針: `docs/product/test-plan.md`
- 既存テストとの対応: `docs/product/test-cases.md`

## 未解決事項

- OpenCompass の生成 config が、実利用する OpenCompass バージョンの dataset 定義に十分かは追加検証が必要。
- `metrics` は設定として保持しているが、runner コマンド生成では直接使っていない。
- 通常実行時に一部 job が失敗した場合、CLI 全体の終了コードをどう扱うかは今後明確化できる。
