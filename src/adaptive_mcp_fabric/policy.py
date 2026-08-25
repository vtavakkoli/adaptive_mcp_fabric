"""Trust-aware policy evaluation for MCP tool calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .models import ExecutionContext, PolicyAction, PolicyDecision, RiskLevel, ToolCapability


@dataclass(frozen=True, slots=True)
class PolicyRule:
    name: str
    action: PolicyAction
    reason: str
    predicate: Callable[[ToolCapability, ExecutionContext], bool]


class PolicyEngine:
    """Composable policy engine with conservative side-effect defaults."""

    def __init__(
        self,
        rules: Iterable[PolicyRule] = (),
        *,
        deny_risks: frozenset[RiskLevel] = frozenset({RiskLevel.CRITICAL}),
        confirm_risks: frozenset[RiskLevel] = frozenset({RiskLevel.HIGH}),
    ) -> None:
        self._rules = tuple(rules)
        self._deny_risks = deny_risks
        self._confirm_risks = confirm_risks

    def evaluate(self, tool: ToolCapability, context: ExecutionContext) -> PolicyDecision:
        for rule in self._rules:
            if rule.predicate(tool, context):
                return PolicyDecision(rule.action, f"{rule.name}: {rule.reason}")
        if tool.risk in self._deny_risks:
            return PolicyDecision(PolicyAction.DENY, f"{tool.risk.value}-risk tool denied by default")
        if tool.risk in self._confirm_risks or not tool.read_only:
            return PolicyDecision(PolicyAction.CONFIRM, "side-effecting or high-risk tool requires explicit approval")
        return PolicyDecision(PolicyAction.ALLOW, "read-only tool allowed by default")

    @staticmethod
    def require_scope(scope: str, *, action: PolicyAction = PolicyAction.DENY) -> PolicyRule:
        return PolicyRule(
            name=f"require-scope:{scope}",
            action=action,
            reason=f"actor is missing required scope '{scope}'",
            predicate=lambda _tool, ctx: scope not in ctx.scopes,
        )

    @staticmethod
    def deny_tag(tag: str) -> PolicyRule:
        return PolicyRule(
            name=f"deny-tag:{tag}",
            action=PolicyAction.DENY,
            reason=f"tool carries denied tag '{tag}'",
            predicate=lambda tool, _ctx: tag in tool.tags,
        )
