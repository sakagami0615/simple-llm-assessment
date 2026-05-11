from __future__ import annotations

from dataclasses import dataclass

from llm_qa_app.providers import ChatProvider


@dataclass
class QAApp:
    provider: ChatProvider

    def answer(self, question: str) -> str:
        prompt = (
            "You are a concise question-answering assistant for LLM application evaluation. "
            "When asked about DeepEval, describe it as a framework for evaluating LLM app output quality. "
            "Answer the user's question directly in Japanese when the question is Japanese.\n\n"
            f"Question: {question}"
        )
        return self.provider.complete(prompt)
