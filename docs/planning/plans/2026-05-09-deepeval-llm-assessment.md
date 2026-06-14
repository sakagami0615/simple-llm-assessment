# DeepEval LLM Model Assessment Plan

## Goal

Keep this repository focused on a simple QA app and a JSONL-driven LLM model evaluation flow.

## Implemented Structure

- `app/llm_qa_app/`: QA app, OpenAI provider, CLI.
- `app/llm_eval/config.py`: model and dataset environment configuration.
- `app/llm_eval/datasets.py`: JSONL loader and schema validation.
- `app/llm_eval/reports.py`: DeepEval result serialization and pass/fail assertion helper.
- `scripts/convert_hf_dataset.py`: optional Hugging Face Dataset to JSONL converter.
- `tests/test_llm_eval.py`: DeepEval-based LLM model quality test.

## Evaluation Flow

1. Load normalized JSONL cases from `LLM_EVAL_DATASET_PATH`.
2. Resolve subject models from `LLM_EVAL_MODELS` or `OPENAI_MODEL`.
3. Resolve the judge model from `DEEPEVAL_MODEL`.
4. Run the QA app once per case and subject model.
5. Evaluate `actual_output` against `input` and `expected_output`.
6. Write one JSON report per subject model.
7. Fail the pytest run when any metric fails.

## Dataset Rules

Allowed JSONL fields:

- `id`
- `input`
- `expected_output`
- `tags`
- `metadata`

`input` and `expected_output` are required non-empty strings. Unknown fields are rejected.

## Verification Commands

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q
poetry check
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run python scripts/convert_hf_dataset.py --help
```

Live model evaluation:

```bash
RUN_LLM_EVAL=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest tests/test_llm_eval.py -v
```
