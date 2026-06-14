# AIDD ドキュメント変換計画

## 目的

既存の README、docs、設定、実装、テストを材料に、AIDD フローに従った正本ドキュメントを `docs/product/` に作成する。

## 前提

- 確認対象は非 ignored ファイルを基本とする。
- `.codex/skills` はユーザー指定により ignored でも確認対象とする。
- それ以外の ignored ファイルは確認しない。
- Git 操作は行わない。

## 作業手順

1. `rg --files` で非 ignored ファイル一覧を確認する。
2. `.codex/skills/aidd-flow` とテンプレートを確認する。
3. README と既存 docs からプロダクト目的、制約、操作、依存関係を抽出する。
4. `src/local_llm_eval/` から実装上の責務とデータフローを抽出する。
5. `tests/` から仕様と検証ケースの対応を抽出する。
6. `docs/product/` に正本 Markdown を作成する。
7. `docs/planning/` に変換メモと作業計画を残す。
8. `docs/superpowers/` に残る specs/plans は、内容を読まずに `docs/planning/` へ移動する。
9. リンク、プレースホルダー、未解決事項、用語の整合性を確認する。
10. 必要な検証コマンドを実行する。

## 作成する正本

- `docs/product/concept.md`
- `docs/product/user-stories.md`
- `docs/product/epics/local-llm-evaluation-orchestrator.md`
- `docs/product/specs/configuration-models.md`
- `docs/product/specs/suite-planning.md`
- `docs/product/specs/runner-adapters.md`
- `docs/product/specs/cli-execution-results.md`
- `docs/product/domain-model.md`
- `docs/product/diagram.md`
- `docs/product/test-plan.md`
- `docs/product/test-cases.md`

## 完了条件

- AIDD の正本ドキュメントが `docs/product/` に置かれている。
- 作業用資料が `docs/planning/` に置かれている。
- spec が epic に紐づいている。
- ドメインモデルとダイアグラムの用語が一致している。
- 意図的な `未解決事項` 以外にプレースホルダーが残っていない。
- 検証コマンドの結果を報告できる。
