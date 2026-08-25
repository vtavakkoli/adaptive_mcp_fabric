"""Adaptive progressive-discovery router."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ExecutionContext, PolicyAction, RankedTool, RouteDecision, ToolCapability
from .policy import PolicyEngine
from .registry import ToolRegistry
from .scoring import SemanticScorer, TokenCosineScorer
from .telemetry import TelemetryStore


@dataclass(frozen=True, slots=True)
class RouterWeights:
    semantic: float = 0.58
    reliability: float = 0.22
    latency: float = 0.08
    token_cost: float = 0.04
    risk: float = 0.08

    def __post_init__(self) -> None:
        values = (self.semantic, self.reliability, self.latency, self.token_cost, self.risk)
        if any(value < 0 for value in values):
            raise ValueError("router weights must be non-negative")
        if sum(values) <= 0:
            raise ValueError("at least one router weight must be positive")


class AdaptiveRouter:
    """Reveal only the best tools from a large MCP catalog."""

    def __init__(
        self,
        registry: ToolRegistry,
        *,
        telemetry: TelemetryStore | None = None,
        scorer: SemanticScorer | None = None,
        policy: PolicyEngine | None = None,
        weights: RouterWeights | None = None,
        latency_reference_ms: float = 2_000.0,
        token_reference: float = 2_000.0,
    ) -> None:
        self.registry = registry
        self.telemetry = telemetry or TelemetryStore()
        self.scorer = scorer or TokenCosineScorer()
        self.policy = policy or PolicyEngine()
        self.weights = weights or RouterWeights()
        self.latency_reference_ms = latency_reference_ms
        self.token_reference = token_reference

    def _rank(self, query: str, tool: ToolCapability) -> RankedTool:
        semantic = self.scorer.score(query, tool.searchable_text)
        stats = self.telemetry.get(tool.key, default_latency_ms=tool.estimated_latency_ms)
        latency_penalty = min(1.0, max(0.0, stats.latency_ms / self.latency_reference_ms))
        token_penalty = min(1.0, max(0.0, tool.estimated_token_cost / self.token_reference))
        risk_penalty = tool.risk.weight
        w = self.weights
        score = (
            w.semantic * semantic
            + w.reliability * stats.reliability
            - w.latency * latency_penalty
            - w.token_cost * token_penalty
            - w.risk * risk_penalty
        )
        return RankedTool(tool, score, semantic, stats.reliability, latency_penalty, token_penalty, risk_penalty)

    def route(
        self,
        query: str,
        *,
        context: ExecutionContext | None = None,
        top_k: int = 5,
        include_confirmation_tools: bool = True,
    ) -> RouteDecision:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        context = context or ExecutionContext()
        ranked: list[RankedTool] = []
        rejected = 0
        for tool in self.registry.all():
            policy = self.policy.evaluate(tool, context)
            if policy.action is PolicyAction.DENY:
                rejected += 1
                continue
            if policy.action is PolicyAction.CONFIRM and not include_confirmation_tools:
                rejected += 1
                continue
            ranked.append(self._rank(query, tool))
        ranked.sort(key=lambda item: (-item.score, item.tool.key))
        return RouteDecision(query, tuple(ranked[:top_k]), len(self.registry), rejected)
