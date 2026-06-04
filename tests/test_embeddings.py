import math

import pytest

from agentic_rag_lab.embeddings import LocalHashEmbeddingProvider


def test_local_hash_embedding_is_deterministic() -> None:
    provider = LocalHashEmbeddingProvider()

    assert provider.embed("RAG retrieval adapter") == provider.embed(
        "RAG retrieval adapter"
    )


def test_local_hash_embedding_is_case_insensitive() -> None:
    provider = LocalHashEmbeddingProvider()

    assert provider.embed("Vector Store") == provider.embed("vector store")


def test_local_hash_embedding_returns_zero_vector_for_empty_text() -> None:
    provider = LocalHashEmbeddingProvider()

    assert provider.embed("   ") == [0.0] * 32


def test_local_hash_embedding_returns_normalized_vector() -> None:
    provider = LocalHashEmbeddingProvider(dimension=16)

    vector = provider.embed("rag retrieval retrieval")

    assert len(vector) == 16
    assert math.sqrt(sum(value * value for value in vector)) == pytest.approx(1.0)


def test_local_hash_embedding_validates_dimension() -> None:
    with pytest.raises(ValueError):
        LocalHashEmbeddingProvider(dimension=0)
