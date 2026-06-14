from __future__ import annotations

from pathlib import Path

from local_llm_eval.planner import EvaluationJob


def build_lm_eval_command(job: EvaluationJob, output_dir: Path) -> list[str]:
    """評価ジョブ用の lm-evaluation-harness コマンドを組み立てる。

    Args:
        job: 実行対象の評価ジョブ。
        output_dir: lm-evaluation-harness が出力を書き込むディレクトリ。

    Returns:
        `lm-eval` に渡すコマンド引数。
    """
    model_args = ",".join(
        [
            f"base_url={job.model.base_url}",
            f"model={job.model.model}",
            "tokenized_requests=False",
        ]
    )
    command = [
        "lm-eval",
        "--model",
        "local-chat-completions",
        "--tasks",
        str(job.benchmark.task),
        "--model_args",
        model_args,
        "--output_path",
        str(output_dir),
        "--log_samples",
        "--apply_chat_template",
    ]
    num_fewshot = job.benchmark.runner_params.get("num_fewshot")
    if num_fewshot is not None:
        command.extend(["--num_fewshot", str(num_fewshot)])
    max_tokens = job.model.generation.get("max_tokens")
    temperature = job.model.generation.get("temperature")
    gen_kwargs = []
    if max_tokens is not None:
        gen_kwargs.append(f"max_gen_toks={max_tokens}")
    if temperature is not None:
        gen_kwargs.append(f"temperature={temperature}")
    if gen_kwargs:
        command.extend(["--gen_kwargs", ",".join(gen_kwargs)])
    return command
