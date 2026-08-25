"""Core domain models for Adaptive MCP Fabric.

The core intentionally uses standard-library dataclasses so routing and policy
logic can be embedded in constrained agents without pulling in a framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class RiskLevel(str, Enum):
    """Coarse risk classification used by the policy engine."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def weight(self) -> float:
        return {
            RiskLevel.LOW: 0.0,
            RiskLevel.MEDIUM: 0.35,
            RiskLevel.HIGH: 0.7,
            RiskLevel.CRITICAL: 1.0,
        }[self]


class PolicyAction(str, Enum):
    """Decision returned by :class:`PolicyEngine`."""

    ALLOW = "allow"
    CONFIRM = "confirm"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class ToolCapability:
    """Normalized capability record for one MCP tool."""

    server_id: str
    name: str
    description: str
    input_schema: Mapping[str, Any] = field(default_factory=dict)
    tags: frozenset[str] = field(default_factory=frozenset)
    risk: RiskLevel = RiskLevel.LOW
    read_only: bool = True
    estimated_latency_ms: float = 250.0
    estimated_token_cost: float = 100.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.server_id}:{self.name}"

    @property
    def searchable_text(self) -> str:
        return " ".join((self.name, self.description, *sorted(self.tags)))


@dataclass(frozen=True, slots=True)
class ToolStats:
    calls: int = 0
    successes: int = 0
    reliability: float = 1.0
    latency_ms: float = 250.0


@dataclass(frozen=True, slots=True)
class RankedTool:
    tool: ToolCapability
    score: float
    semantic_score: float
    reliability_score: float
    latency_penalty: float
    token_penalty: float
    risk_penalty: float


@dataclass(frozen=True, slots=True)
class RouteDecision:
    query: str
    selected: tuple[RankedTool, ...]
    considered: int
    rejected_by_policy: int = 0


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    actor: str = "anonymous"
    tenant: str | None = None
    scopes: frozenset[str] = field(default_factory=frozenset)
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    action: PolicyAction
    reason: str


@dataclass(frozen=True, slots=True)
class PlanStep:
    id: str
    tool_key: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    steps: tuple[PlanStep, ...]

    def ids(self) -> tuple[str, ...]:
        return tuple(step.id for step in self.steps)


@dataclass(frozen=True, slots=True)
class ToolResult:
    step_id: str
    tool_key: str
    ok: bool
    output: Any = None
    error: str | None = None
    latency_ms: float = 0.0


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    results: tuple[ToolResult, ...]

    @property
    def ok(self) -> bool:
        return all(result.ok for result in self.results)

    def by_step(self) -> dict[str, ToolResult]:
        return {result.step_id: result for result in self.results}
