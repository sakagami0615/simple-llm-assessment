from __future__ import annotations

import argparse

from llm_qa_app.providers import OpenAIChatProvider
from llm_qa_app.qa_app import QAApp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-app")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ask_parser = subparsers.add_parser("ask", help="Ask the QA app a question")
    ask_parser.add_argument("question")

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "ask":
        app = QAApp(provider=OpenAIChatProvider())
        print(app.answer(args.question))
