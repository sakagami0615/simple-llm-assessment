from __future__ import annotations

import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from local_llm_eval.planner import EvaluationJob, EvaluationPlan
from local_llm_eval.results import write_json
from local_llm_eval.runners.lm_evaluation_harness import build_lm_eval_command
from local_llm_eval.runners.opencompass import build_opencompass_command


CommandRunner = Callable[[list[str], Path, dict[str, str]], int]


@dataclass(frozen=True)
class ExecutionResult:
    """完了したオーケストレーション実行の結果メタデータ。

    Attributes:
        run_dir: run メタデータ、summary、raw 出力を格納するディレクトリ。
    """

    run_dir: Path


def default_command_runner(command: list[str], cwd: Path, env: dict[str, str]) -> int:
    """外部コマンドを実行する。

    Args:
        command: 実行するコマンドと引数。
        cwd: コマンドの作業ディレクトリ。
        env: コマンドへ渡す環境変数。

    Returns:
        プロセス終了コード。
    """
    completed = subprocess.run(command, cwd=cwd, env=env, check=False)
    return completed.returncode


def execute_plan(
    plan: EvaluationPlan,
    runs_dir: Path = Path("runs"),
    dry_run: bool = False,
    command_runner: CommandRunner = default_command_runner,
) -> ExecutionResult:
    """評価計画内の全ジョブを実行、または dry-run する。

    Args:
        plan: 解決済みの評価計画。
        runs_dir: run 出力を格納する基準ディレクトリ。
        dry_run: true の場合、コマンドを実行せず記録だけ行う。
        command_runner: 外部コマンド実行に使う関数。

    Returns:
        作成した run ディレクトリのメタデータ。
    """
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    run_dir = runs_dir / f"{timestamp}-{plan.suite.id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, object] = {
        "suite_id": plan.suite.id,
        "run_dir": str(run_dir),
        "dry_run": dry_run,
        "jobs": [],
    }

    write_json(run_dir / "run.yaml.json", {"plan": asdict(plan)})

    for job in plan.jobs:
        job_dir = run_dir / "raw" / job.output_name
        job_dir.mkdir(parents=True, exist_ok=True)
        command = _build_command(job, job_dir)
        if dry_run:
            status = "skipped"
            exit_code = None
        else:
            exit_code = command_runner(command, Path.cwd(), os.environ.copy())
            status = "success" if exit_code == 0 else "failed"
        summary["jobs"].append(
            {
                "model_id": job.model.id,
                "benchmark_id": job.benchmark.id,
                "runner": job.benchmark.runner,
                "status": status,
                "exit_code": exit_code,
                "command": command,
                "raw_output_path": str(job_dir),
            }
        )

    write_json(run_dir / "summary.json", summary)
    return ExecutionResult(run_dir=run_dir)


def _build_command(job: EvaluationJob, job_dir: Path) -> list[str]:
    if job.benchmark.runner == "lm-evaluation-harness":
        return build_lm_eval_command(job, job_dir)
    if job.benchmark.runner == "OpenCompass":
        return build_opencompass_command(job, job_dir)
    raise ValueError(f"Unsupported runner: {job.benchmark.runner}")
