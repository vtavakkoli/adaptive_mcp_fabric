"""Execution-plan validation and dependency scheduling."""

from collections import defaultdict, deque
from collections.abc import Iterable

from .models import ExecutionPlan, PlanStep


class PlanValidationError(ValueError):
    pass


class DAGPlanner:
    def build(self, steps: Iterable[PlanStep]) -> ExecutionPlan:
        plan = ExecutionPlan(tuple(steps))
        self.validate(plan)
        return plan

    def validate(self, plan: ExecutionPlan) -> None:
        ids = [step.id for step in plan.steps]
        if len(ids) != len(set(ids)):
            raise PlanValidationError("step ids must be unique")
        known = set(ids)
        for step in plan.steps:
            missing = set(step.depends_on) - known
            if missing:
                raise PlanValidationError(f"step {step.id!r} depends on unknown steps: {sorted(missing)}")
            if step.id in step.depends_on:
                raise PlanValidationError(f"step {step.id!r} cannot depend on itself")
        self.layers(plan)

    def layers(self, plan: ExecutionPlan) -> tuple[tuple[PlanStep, ...], ...]:
        by_id = {step.id: step for step in plan.steps}
        indegree = {step.id: len(step.depends_on) for step in plan.steps}
        children: dict[str, list[str]] = defaultdict(list)
        for step in plan.steps:
            for parent in step.depends_on:
                children[parent].append(step.id)
        current = deque(sorted(step_id for step_id, degree in indegree.items() if degree == 0))
        layers: list[tuple[PlanStep, ...]] = []
        visited = 0
        while current:
            layer_ids = tuple(current)
            current.clear()
            layer = tuple(by_id[step_id] for step_id in layer_ids)
            layers.append(layer)
            visited += len(layer)
            next_ids: list[str] = []
            for step_id in layer_ids:
                for child in children[step_id]:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        next_ids.append(child)
            current.extend(sorted(next_ids))
        if visited != len(plan.steps):
            raise PlanValidationError("execution plan contains a dependency cycle")
        return tuple(layers)
