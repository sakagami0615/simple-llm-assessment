# DeepEval LLM Assessment Design

## Goal

Build a small Python environment that contains:

- A simple question-answering LLM application.
- A local DeepEval-based evaluation runner.
- A test data interface that can be reused by other LLM applications, including future RAG applications.

The first application is a non-RAG QA CLI using OpenAI. The evaluation environment is DeepEval-first and uses DeepEval's `LLMTestCase` as the central evaluation model.

## Constraints

- Use Python with the current `pyproject.toml` setting, `requires-python = ">=3.14,<4.0"`.
- If DeepEval, OpenAI SDK, or related dependencies fail to resolve under Python 3.14, lower the Python version as a follow-up compatibility fix.
- Use Poetry as the project packaging tool.
- Keep evaluation local for now. Do not add CI or pytest integration in the first implementation.
- Use JSONL as the standard portable dataset format.
- Do not integrate Hugging Face Datasets directly in the first implementation. Public datasets can be converted to JSONL before evaluation.
- The workspace is not currently an initialized Git repository, so no commit is required for this design phase.

## Architecture

The project will be split into an application package and an evaluation package.

```text
src/
  llm_app/
    __init__.py
    cli.py
    providers.py
    qa_app.py
  llm_eval/
    __init__.py
    cli.py
    datasets.py
    app_runner.py
    deepeval_runner.py
    metrics.py
    reports.py
data/
  eval_cases/
    qa_sample.jsonl
    rag_sample.jsonl
reports/
  .gitkeep
```

### Application Package

`llm_app` provides the first simple QA application.

- `qa_app.py` exposes a small function or class that accepts a question and returns an answer string.
- `providers.py` contains the OpenAI provider implementation and hides direct SDK calls from the app logic.
- `cli.py` exposes a command such as `llm-app ask "question"`.

The provider boundary should be thin, but explicit enough that another provider can be added later without changing evaluation code.

### Evaluation Package

`llm_eval` provides a reusable DeepEval runner.

- `datasets.py` reads JSONL records and validates required fields.
- `app_runner.py` adapts an application into a callable evaluation target.
- `deepeval_runner.py` builds DeepEval `LLMTestCase` objects and runs metrics.
- `metrics.py` defines DeepEval metric presets.
- `reports.py` writes local evaluation reports.
- `cli.py` exposes a command such as `llm-eval run --dataset data/eval_cases/qa_sample.jsonl --app qa`.

The evaluation package is intentionally DeepEval-native. It does not hide DeepEval behind a generic evaluation abstraction.

## Data Flow

```text
JSONL dataset
  input
  expected_output
  retrieval_context optional
        |
        v
AppRunner
  input -> actual_output
        |
        v
DeepEval LLMTestCase
        |
        v
DeepEval metrics
        |
        v
local report
```

The JSONL dataset contains test inputs and expected outputs. `actual_output` is normally generated at evaluation time by running the application.

## JSONL Dataset Format

Each line is a JSON object with names aligned to DeepEval `LLMTestCase` where practical.

Required fields:

- `input`: user input, prompt, or question.

Usually required for QA evaluation:

- `expected_output`: expected answer or reference answer.

Optional fields:

- `id`: stable case identifier.
- `retrieval_context`: list of context strings for RAG-style evaluation.
- `tags`: list of strings for grouping cases.
- `metadata`: object for dataset-specific values.
- `actual_output`: optional debug or fixed-output field.

Example QA case:

```json
{"id":"qa_001","input":"DeepEvalとは何ですか？","expected_output":"LLMアプリケーションの出力品質を評価するためのフレームワークです。","tags":["qa","baseline"]}
```

Example RAG-shaped case:

```json
{"id":"rag_001","input":"経費精算の期限は？","expected_output":"発生日から30日以内です。","retrieval_context":["経費精算は発生日から30日以内に申請する必要があります。"],"tags":["rag"]}
```

If `actual_output` is present in JSONL, the first implementation should still run the target app and use the newly generated output by default. A later option can add a flag to evaluate fixed outputs without app execution.

## DeepEval Integration

The runner builds `LLMTestCase` instances after app execution.

For QA cases:

- `input` comes from JSONL.
- `actual_output` comes from the app runner.
- `expected_output` comes from JSONL.

For RAG-shaped cases:

- `retrieval_context` is passed through when present.
- RAG-specific metrics can run only when the required context exists.

Initial metric presets:

- QA answer relevance: `AnswerRelevancyMetric`.
- Expected-answer comparison: `GEval` configured as an LLM-as-a-judge correctness check.
- RAG readiness: `FaithfulnessMetric` and `ContextualRelevancyMetric` defined as optional presets for cases with `retrieval_context`.

The first local CLI can default to a QA preset and allow selecting a RAG preset later.

## Configuration

Runtime configuration should come from environment variables, optionally loaded from `.env`.

```text
OPENAI_API_KEY=...
OPENAI_MODEL=...
DEEPEVAL_MODEL=...
```

Expected defaults:

- `OPENAI_MODEL` defaults to a small current OpenAI chat model if not set.
- `DEEPEVAL_MODEL` can default to the same model unless DeepEval requires a different configuration.

Exact model names should be confirmed during implementation because OpenAI and DeepEval model support can change.

## CLI Behavior

Application CLI:

```text
llm-app ask "DeepEvalとは何ですか？"
```

Evaluation CLI:

```text
llm-eval run --dataset data/eval_cases/qa_sample.jsonl --app qa
```

Expected evaluation behavior:

- Load dataset records.
- Run the configured app for each record.
- Build `LLMTestCase` objects.
- Run the selected DeepEval metrics.
- Print a concise console summary.
- Write a JSON report under `reports/`.

## Report Output

The report should be useful for local inspection and simple comparison between runs.

Minimum report fields:

- Run timestamp.
- Dataset path.
- App name.
- Metric preset.
- Per-case results, including case id, input, actual output, metric names, scores, pass/fail status if available, and reasons if provided by DeepEval.
- Aggregate summary, including case count and metric-level averages where available.

## Initial Scope

Included:

- OpenAI-backed simple QA CLI.
- JSONL evaluation dataset loader.
- DeepEval `LLMTestCase` centered evaluation runner.
- QA sample JSONL.
- RAG-shaped sample JSONL to prove the data interface can represent context.
- Local console and JSON report output.
- Basic usage documentation.

Excluded:

- pytest integration.
- CI integration.
- Hugging Face Datasets direct loading.
- FastAPI or web API.
- Full RAG implementation.
- Vector database integration.
- Provider implementations beyond OpenAI.

## Error Handling

Dataset errors should fail before any LLM calls when possible.

- Missing `input`: fail validation.
- Missing `expected_output` for QA preset: fail validation.
- Invalid `retrieval_context`: fail validation if present and not a list of strings.
- Empty dataset: fail with a clear message.
- Unknown app name or metric preset: fail with supported choices.

LLM and DeepEval runtime errors should include the case id when available, so the failing input can be found quickly.

## Testing Strategy

The first implementation does not add pytest-based DeepEval evaluation. It should still include focused local verification where practical:

- Unit tests or simple checks for JSONL parsing and validation.
- A small sample dataset that can be run manually.
- A mock or deterministic app runner path may be added if needed to verify the evaluation pipeline without spending API calls.

DeepEval metric execution requires LLM access and should remain a local command in the first version.

## Future Extensions

Likely follow-ups:

- Add `--use-existing-actual-output` to evaluate precomputed model outputs.
- Add CSV or mapping-based dataset conversion into the JSONL format.
- Add Hugging Face Datasets ingestion after the JSONL interface is stable.
- Add pytest integration for selected stable checks.
- Add a real RAG application runner that returns both `actual_output` and `retrieval_context`.
- Add provider selection beyond OpenAI.
