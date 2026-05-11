from __future__ import annotations

from dataclasses import dataclass
import os
from collections.abc import Iterable

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStore
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


@dataclass(frozen=True)
class RAGResult:
    answer: str
    retrieval_context: list[str]


class LangChainRAGApp:
    def __init__(
        self,
        documents: Iterable[Document],
        model: str | None = None,
        embeddings: Embeddings | None = None,
        chat_model: BaseChatModel | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        load_dotenv()
        self._documents = list(documents)
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self._embeddings = embeddings or OpenAIEmbeddings()
        self._vector_store = vector_store or Chroma.from_documents(
            documents=self._documents,
            embedding=self._embeddings,
        )
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
        llm = chat_model or ChatOpenAI(model=self._model, temperature=0)
        self._chain = prompt | llm | StrOutputParser()

    @classmethod
    def from_contexts(
        cls,
        contexts: Iterable[str],
        model: str | None = None,
        embeddings: Embeddings | None = None,
        chat_model: BaseChatModel | None = None,
    ) -> LangChainRAGApp:
        return cls(
            (Document(page_content=context) for context in contexts),
            model=model,
            embeddings=embeddings,
            chat_model=chat_model,
        )

    def answer(self, question: str, top_k: int = 1) -> RAGResult:
        retrieved = self._retrieve(question, top_k=top_k)
        context = "\n".join(document.page_content for document in retrieved)
        answer = self._chain.invoke({"context": context, "question": question}).strip()
        return RAGResult(
            answer=answer,
            retrieval_context=[document.page_content for document in retrieved],
        )

    def _retrieve(self, question: str, top_k: int) -> list[Document]:
        return self._vector_store.similarity_search(question, k=top_k)
