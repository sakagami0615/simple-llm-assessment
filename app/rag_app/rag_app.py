from __future__ import annotations

from dataclasses import dataclass
import os
import re
from collections.abc import Iterable

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


@dataclass(frozen=True)
class RAGResult:
    answer: str
    retrieval_context: list[str]


class LangChainRAGApp:
    def __init__(self, documents: Iterable[Document], model: str | None = None) -> None:
        load_dotenv()
        self._documents = list(documents)
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a concise RAG assistant. Answer only from the provided context. "
                    "If the context is Japanese, answer in Japanese.",
                ),
                ("human", "Context:\n{context}\n\nQuestion: {question}"),
            ]
        )
        self._chain = prompt | ChatOpenAI(model=self._model, temperature=0) | StrOutputParser()

    @classmethod
    def from_contexts(cls, contexts: Iterable[str], model: str | None = None) -> LangChainRAGApp:
        return cls((Document(page_content=context) for context in contexts), model=model)

    def answer(self, question: str, top_k: int = 1) -> RAGResult:
        retrieved = self._retrieve(question, top_k=top_k)
        context = "\n".join(document.page_content for document in retrieved)
        answer = self._chain.invoke({"context": context, "question": question}).strip()
        return RAGResult(
            answer=answer,
            retrieval_context=[document.page_content for document in retrieved],
        )

    def _retrieve(self, question: str, top_k: int) -> list[Document]:
        query_terms = _terms(question)
        ranked = sorted(
            self._documents,
            key=lambda document: _score(query_terms, document.page_content),
            reverse=True,
        )
        return ranked[:top_k]


def _terms(text: str) -> set[str]:
    normalized = text.lower()
    terms = set(re.findall(r"[A-Za-z0-9_]+|[一-龥ぁ-んァ-ン]+", normalized))
    compact = re.sub(r"\s+", "", normalized)
    terms.update(compact[index : index + 2] for index in range(max(0, len(compact) - 1)))
    return terms


def _score(query_terms: set[str], text: str) -> int:
    text_terms = _terms(text)
    return len(query_terms & text_terms)
