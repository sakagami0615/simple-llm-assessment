from __future__ import annotations

import os
from typing import Protocol

from dotenv import load_dotenv
from openai import OpenAI


class ChatProvider(Protocol):
    def complete(self, prompt: str) -> str:
        """Return a text completion for a user prompt."""


class OpenAIChatProvider:
    def __init__(self, model: str | None = None) -> None:
        load_dotenv()
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self._client = OpenAI()

    def complete(self, prompt: str) -> str:
        response = self._client.responses.create(
            model=self._model,
            input=prompt,
        )
        return response.output_text.strip()
