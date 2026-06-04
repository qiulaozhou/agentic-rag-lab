"""Deterministic local embedding provider."""

from __future__ import annotations

import hashlib
import math
import re

_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


class LocalHashEmbeddingProvider:
    """Create stable bag-of-words embeddings without external services."""

    def __init__(self, dimension: int = 32) -> None:
        if dimension <= 0:
            raise ValueError("dimension must be greater than 0")
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        tokens = _TOKEN_PATTERN.findall(text.lower())
        vector = [0.0] * self.dimension

        for token in tokens:
            index = _stable_index(token, self.dimension)
            vector[index] += 1.0

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector

        return [value / magnitude for value in vector]


def _stable_index(token: str, dimension: int) -> int:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big") % dimension
