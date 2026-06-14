# Appendix

## 依存関係

このプロジェクトは Python 3.14 を指定しています。

CLI 本体は Python 3.14 で動作確認できますが、OpenCompass が依存する `torch` などは Python 3.14 対応 wheel がまだ揃っていない場合があります。

その場合は、以下のように使い分けてください。

- CLI 本体の開発・設定検証・dry-run: Python 3.14
- lm-evaluation-harness / OpenCompass 本体をインストールして実評価する環境: Python 3.13 以下

```bash
poetry install
poetry run local-llm-eval validate config/suites/baseline.yaml
poetry run local-llm-eval run config/suites/baseline.yaml --dry-run
```

実評価環境では、Python 3.13 以下の環境で eval dependency group をインストールします。

```bash
poetry install --with eval
```
