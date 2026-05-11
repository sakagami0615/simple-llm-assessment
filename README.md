# simple-llm-assessment

このプロジェクトは、OpenAI を使った簡易的な質問回答アプリ、LangChain を使った簡易RAGアプリ、DeepEval による LLM 性能評価テストを含みます。

`app/` は本番デプロイ対象のアプリケーションコード、`tests/` は DeepEval による性能評価テストです。

## セットアップ

```bash
poetry install --with eval
cp .env.example .env
```

`.env` に `OPENAI_API_KEY` を設定してください。

このプロジェクトでは現在 `requires-python = ">=3.14,<4.0"` を指定しています。Python 3.14 対応が原因で依存関係の解決に失敗する場合は、互換性対応として Python バージョンを下げてください。

## QAアプリの実行

```bash
poetry run llm-app ask "DeepEvalとは何ですか？"
```

## LLM性能評価の実行

```bash
RUN_LLM_EVAL=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_llm_eval.py tests/test_rag_eval.py -v
```

`OPENAI_API_KEY` が未設定、または `RUN_LLM_EVAL=1` が未指定の場合、この評価テストは skip されます。
実行後、`reports/` 配下に `deepeval-qa-report-*.json` と `deepeval-rag-report-*.json` が出力されます。

## ローカルチェック

DeepEval は socket アクセスを必要とする pytest プラグインをインストールする場合があります。制限された sandbox でテストを実行する場合は、pytest プラグインの自動ロードを無効化してください。

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_llm_eval.py tests/test_rag_eval.py -v
```

## ローカルで検証済みのコマンド

- `poetry install`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_llm_eval.py tests/test_rag_eval.py -v`
- `poetry run python -c "from llm_qa_app.cli import main as app_main; from rag_app.rag_app import LangChainRAGApp; print(app_main, LangChainRAGApp)"`
- `poetry run llm-app --help`

OpenAI を使うアプリ実行と DeepEval metric の実行には `OPENAI_API_KEY` が必要です。この環境では、これらのコマンドは実行していません。
