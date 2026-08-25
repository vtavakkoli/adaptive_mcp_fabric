"""Lightweight adaptive telemetry for tool reliability and latency."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from .models import ToolStats


@dataclass(slots=True)
class _MutableStats:
    calls: int = 0
    successes: int = 0
    latency_ms: float = 250.0


class TelemetryStore:
    def __init__(self, smoothing: float = 0.2) -> None:
        if not 0.0 < smoothing <= 1.0:
            raise ValueError("smoothing must be in (0, 1]")
        self._smoothing = smoothing
        self._stats: dict[str, _MutableStats] = {}
        self._lock = RLock()

    def record(self, tool_key: str, *, ok: bool, latency_ms: float) -> None:
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        with self._lock:
            stats = self._stats.setdefault(tool_key, _MutableStats(latency_ms=latency_ms))
            stats.calls += 1
            stats.successes += int(ok)
            alpha = self._smoothing
            stats.latency_ms = alpha * latency_ms + (1.0 - alpha) * stats.latency_ms

    def get(self, tool_key: str, *, default_latency_ms: float = 250.0) -> ToolStats:
        with self._lock:
            stats = self._stats.get(tool_key)
            if stats is None:
                return ToolStats(latency_ms=default_latency_ms)
            reliability = stats.successes / stats.calls if stats.calls else 1.0
            return ToolStats(stats.calls, stats.successes, reliability, stats.latency_ms)

    def snapshot(self) -> dict[str, ToolStats]:
        with self._lock:
            return {key: self.get(key, default_latency_ms=value.latency_ms) for key, value in self._stats.items()}
