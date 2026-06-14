from __future__ import annotations

from pathlib import Path

from local_llm_eval.planner import EvaluationJob


def build_opencompass_command(job: EvaluationJob, output_dir: Path) -> list[str]:
    """OpenCompass コマンドと生成 config を組み立てる。

    Args:
        job: 実行対象の評価ジョブ。
        output_dir: OpenCompass が出力を書き込むディレクトリ。

    Returns:
        `opencompass` に渡すコマンド引数。
    """
    config_path = output_dir / "opencompass_config.py"
    output_dir.mkdir(parents=True, exist_ok=True)
    config_path.write_text(_render_config(job), encoding="utf-8")
    return [
        "opencompass",
        "--config",
        str(config_path),
        "--work-dir",
        str(output_dir),
    ]


def _render_config(job: EvaluationJob) -> str:
    dataset_path = job.benchmark.dataset or ""
    max_out_len = job.model.generation.get("max_tokens", 512)
    temperature = job.model.generation.get("temperature", 0)
    api_key_expr = "os.environ.get(%r, 'EMPTY')" % (job.model.api_key_env or "LOCAL_LLM_API_KEY")
    return f'''import os

from opencompass.models import OpenAI

models = [
    dict(
        type=OpenAI,
        path={job.model.model!r},
        openai_api_base={job.model.base_url!r},
        key={api_key_expr},
        abbr={job.model.id!r},
        max_out_len={max_out_len!r},
        batch_size=1,
        temperature={temperature!r},
        run_cfg=dict(num_gpus=0),
    )
]

datasets = [
    dict(
        abbr={job.benchmark.id!r},
        path={dataset_path!r},
        type={job.benchmark.dataset_format!r},
        evaluator={job.benchmark.evaluator!r},
    )
]
'''
