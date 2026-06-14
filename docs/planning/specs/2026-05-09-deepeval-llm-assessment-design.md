# DeepEval LLM Model Assessment Design

## Goal

Build a small OpenAI-backed QA application and a local DeepEval assessment flow focused only on LLM model output quality.

The assessment should make model runs comparable by using one stable JSONL dataset format and one stable JSON report schema.

## Scope

In scope:

- QA application wrapper in `app/llm_qa_app/`.
- Evaluation helpers in `app/llm_eval/`.
- JSONL dataset loading and validation.
- DeepEval metrics for answer relevancy and correctness.
- JSON report output with model and dataset metadata.
- Optional Hugging Face Dataset to JSONL conversion script.

Out of scope:

- Retrieval pipelines.
- Context-grounded metrics.
- Vector stores.
- Framework-specific retrieval application code.

## Dataset Format

Each JSONL row is one evaluation case.

Required fields:

- `input`: prompt or question sent to the application.
- `expected_output`: reference answer used by correctness evaluation.

Optional fields:

- `id`: stable case identifier.
- `tags`: list of string labels.
- `metadata`: object for source, split, original identifiers, or benchmark notes.

Unsupported fields are rejected so that benchmark data is normalized before evaluation.

Example:

```json
{"id":"qa_001","input":"DeepEvalとは何ですか？","expected_output":"DeepEvalはLLMアプリケーションの出力品質を評価するためのフレームワークです。","tags":["qa","baseline"]}
```

## Model Configuration

- `OPENAI_MODEL`: single subject model.
- `LLM_EVAL_MODELS`: comma-separated subject model list.
- `DEEPEVAL_MODEL`: judge model used by DeepEval.
- `LLM_EVAL_DATASET_PATH`: JSONL dataset path.

One test run can evaluate one or more subject models. Each subject model writes a report with the same schema.

## Report Schema

Reports are written to `reports/deepeval-llm-report-*.json` and include:

- `app_name`
- `dataset_path`
- `subject_model`
- `judge_model`
- `run_timestamp`
- `cases`
- `summary.case_count`
- `summary.metric_averages`

## Verification

Non-network verification uses:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 poetry run pytest -q
poetry check
```

Live DeepEval execution requires `RUN_LLM_EVAL=1` and `OPENAI_API_KEY`.
