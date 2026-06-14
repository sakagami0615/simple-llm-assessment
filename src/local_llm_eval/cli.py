from __future__ import annotations

import argparse
import sys
from pathlib import Path

from local_llm_eval.config import ConfigError
from local_llm_eval.executor import execute_plan
from local_llm_eval.planner import plan_suite


def build_parser() -> argparse.ArgumentParser:
    """コマンドライン引数パーサーを構築する。

    Returns:
        `local-llm-eval` コマンド用に設定済みの引数パーサー。
    """
    parser = argparse.ArgumentParser(prog="local-llm-eval")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("suite")

    run = subparsers.add_parser("run")
    run.add_argument("suite")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--runs-dir", default="runs")

    return parser


def main(argv: list[str] | None = None) -> int:
    """local-llm-eval CLI を実行する。

    Args:
        argv: 任意のコマンドライン引数。省略時は argparse が `sys.argv`
            から読み込む。

    Returns:
        プロセス終了コード。
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        plan = plan_suite(args.suite)
        if args.command == "validate":
            print(f"valid: {plan.suite.id}")
            return 0
        if args.command == "run":
            result = execute_plan(plan, runs_dir=Path(args.runs_dir), dry_run=args.dry_run)
            print(f"run_dir: {result.run_dir}")
            return 0
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
