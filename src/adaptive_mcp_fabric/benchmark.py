"""Synthetic benchmark utilities for progressive-discovery experiments."""

import random
from dataclasses import dataclass

from .models import RiskLevel, ToolCapability
from .registry import ToolRegistry
from .router import AdaptiveRouter


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    query: str
    expected_tool_key: str


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    cases: int
    top1_accuracy: float
    top5_recall: float


def synthetic_catalog(size: int, *, seed: int = 7) -> tuple[ToolCapability, ...]:
    if size < 1:
        raise ValueError("size must be >= 1")
    random.seed(seed)
    domains = ("weather", "math", "files", "database", "github", "calendar", "search")
    tools = []
    for index in range(size):
        domain = domains[index % len(domains)]
        tools.append(ToolCapability(server_id=f"server-{index // 20}", name=f"{domain}_{index}", description=f"{domain} operation for {domain} requests and structured {domain} tasks", tags=frozenset({domain, "synthetic"}), risk=RiskLevel.LOW, estimated_latency_ms=random.uniform(20, 800), estimated_token_cost=random.uniform(40, 300)))
    return tuple(tools)


def evaluate(router: AdaptiveRouter, cases: tuple[BenchmarkCase, ...]) -> BenchmarkResult:
    if not cases:
        return BenchmarkResult(0, 0.0, 0.0)
    top1 = top5 = 0
    for case in cases:
        keys = [ranked.tool.key for ranked in router.route(case.query, top_k=5).selected]
        top1 += int(bool(keys) and keys[0] == case.expected_tool_key)
        top5 += int(case.expected_tool_key in keys)
    total = len(cases)
    return BenchmarkResult(total, top1 / total, top5 / total)


def build_router_for_catalog(size: int) -> AdaptiveRouter:
    registry = ToolRegistry()
    registry.register_many(synthetic_catalog(size))
    return AdaptiveRouter(registry)
