from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from rag_app.rag_app import LangChainRAGApp


class KeywordEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        return [
            float("経費" in text or "期限" in text),
            float("レポート" in text or "保存" in text),
        ]


def test_rag_app_retrieves_context_with_vector_similarity():
    app = LangChainRAGApp.from_contexts(
        [
            "ローカル評価のJSONレポートはreportsディレクトリに保存されます。",
            "経費精算は発生日から30日以内に申請する必要があります。",
        ],
        embeddings=KeywordEmbeddings(),
        chat_model=FakeListChatModel(responses=["発生日から30日以内です。"]),
    )

    result = app.answer("経費精算の期限は？")

    assert result.answer == "発生日から30日以内です。"
    assert result.retrieval_context == [
        "経費精算は発生日から30日以内に申請する必要があります。",
    ]


def test_rag_app_reuses_persisted_chroma_collection(tmp_path):
    persist_directory = tmp_path / "chroma"

    LangChainRAGApp.from_contexts(
        [
            "ローカル評価のJSONレポートはreportsディレクトリに保存されます。",
            "経費精算は発生日から30日以内に申請する必要があります。",
        ],
        embeddings=KeywordEmbeddings(),
        chat_model=FakeListChatModel(responses=["unused"]),
        persist_directory=persist_directory,
    )

    app = LangChainRAGApp.from_contexts(
        [],
        embeddings=KeywordEmbeddings(),
        chat_model=FakeListChatModel(responses=["発生日から30日以内です。"]),
        persist_directory=persist_directory,
    )

    result = app.answer("経費精算の期限は？")

    assert result.retrieval_context == [
        "経費精算は発生日から30日以内に申請する必要があります。",
    ]
