"""Pluggable semantic scoring primitives."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Protocol

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_./:-]+")


class SemanticScorer(Protocol):
    def score(self, query: str, document: str) -> float:
        """Return a normalized similarity in [0, 1]."""


class TokenCosineScorer:
    """Dependency-free deterministic cosine scorer."""

    @staticmethod
    def _vector(text: str) -> Counter[str]:
        return Counter(token.lower() for token in _TOKEN_RE.findall(text))

    def score(self, query: str, document: str) -> float:
        left, right = self._vector(query), self._vector(document)
        if not left or not right:
            return 0.0
        dot = sum(value * right.get(token, 0) for token, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if not left_norm or not right_norm:
            return 0.0
        return max(0.0, min(1.0, dot / (left_norm * right_norm)))
