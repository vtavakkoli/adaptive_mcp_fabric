"""Trust-aware concurrent execution of MCP tool DAGs."""

from __future__ import annotations

import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from .models import ExecutionContext, ExecutionPlan, ExecutionReport, PlanStep, PolicyAction, ToolResult
from .planner import DAGPlanner
from .policy import PolicyEngine
from .registry import ToolRegistry
from .telemetry import TelemetryStore


class ToolInvoker(Protocol):
    async def __call__(self, server_id: str, tool_name: str, arguments: dict[str, Any]) -> Any: ...


ConfirmationCallback = Callable[[PlanStep, str], bool | Awaitable[bool]]


class ExecutionDenied(RuntimeError):
    pass


class FabricExecutor:
    def __init__(self, registry: ToolRegistry, invoker: ToolInvoker, *, telemetry=None, policy=None, planner=None) -> None:
        self.registry = registry
        self.invoker = invoker
        self.telemetry = telemetry or TelemetryStore()
        self.policy = policy or PolicyEngine()
        self.planner = planner or DAGPlanner()

    async def _approved(self, step: PlanStep, reason: str, callback: ConfirmationCallback | None) -> bool:
        if callback is None:
            return False
        result = callback(step, reason)
        if inspect.isawaitable(result):
            return bool(await result)
        return bool(result)

    async def _run_step(self, step, context, confirm) -> ToolResult:
        tool = self.registry.get(step.tool_key)
        decision = self.policy.evaluate(tool, context)
        if decision.action is PolicyAction.DENY:
            raise ExecutionDenied(f"{step.id}: {decision.reason}")
        if decision.action is PolicyAction.CONFIRM and not await self._approved(step, decision.reason, confirm):
            return ToolResult(step.id, tool.key, False, error=f"confirmation required: {decision.reason}")
        started = time.perf_counter()
        try:
            output = await self.invoker(tool.server_id, tool.name, dict(step.arguments))
            latency_ms = (time.perf_counter() - started) * 1000.0
            self.telemetry.record(tool.key, ok=True, latency_ms=latency_ms)
            return ToolResult(step.id, tool.key, True, output=output, latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = (time.perf_counter() - started) * 1000.0
            self.telemetry.record(tool.key, ok=False, latency_ms=latency_ms)
            return ToolResult(step.id, tool.key, False, error=f"{type(exc).__name__}: {exc}", latency_ms=latency_ms)

    async def execute(self, plan: ExecutionPlan, *, context=None, confirm=None, stop_on_failure: bool = True) -> ExecutionReport:
        self.planner.validate(plan)
        context = context or ExecutionContext()
        results: dict[str, ToolResult] = {}
        for layer in self.planner.layers(plan):
            runnable = []
            for step in layer:
                failed_parent = next((parent for parent in step.depends_on if parent in results and not results[parent].ok), None)
                if failed_parent is not None:
                    results[step.id] = ToolResult(step.id, step.tool_key, False, error=f"dependency failed: {failed_parent}")
                else:
                    runnable.append(step)
            if runnable:
                completed = await asyncio.gather(*(self._run_step(step, context, confirm) for step in runnable))
                results.update({result.step_id: result for result in completed})
            if stop_on_failure and any(not result.ok for result in results.values()):
                for step in plan.steps:
                    if step.id not in results:
                        results[step.id] = ToolResult(step.id, step.tool_key, False, error="execution stopped after previous failure")
                break
        return ExecutionReport(tuple(results[step.id] for step in plan.steps))
