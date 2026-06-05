from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
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
        persist_directory: str | Path | None = None,
        collection_name: str = "rag_app",
    ) -> None:
        load_dotenv()
        self._documents = list(documents)
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self._embeddings = embeddings or OpenAIEmbeddings()
        self._vector_store = vector_store or self._build_vector_store(
            persist_directory=persist_directory,
            collection_name=collection_name,
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
        persist_directory: str | Path | None = None,
        collection_name: str = "rag_app",
    ) -> LangChainRAGApp:
        return cls(
            (Document(page_content=context) for context in contexts),
            model=model,
            embeddings=embeddings,
            chat_model=chat_model,
            persist_directory=persist_directory,
            collection_name=collection_name,
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

    def _build_vector_store(
        self,
        persist_directory: str | Path | None,
        collection_name: str,
    ) -> Chroma:
        if persist_directory is None:
            return Chroma.from_documents(
                documents=self._documents,
                embedding=self._embeddings,
                collection_name=collection_name,
            )

        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self._embeddings,
            persist_directory=str(persist_directory),
        )
        if self._documents and _is_collection_empty(vector_store):
            vector_store.add_documents(self._documents)
        return vector_store


def _is_collection_empty(vector_store: Chroma) -> bool:
    collection = vector_store.get(limit=1, include=[])
    ids = collection.get("ids", [])
    return not ids
