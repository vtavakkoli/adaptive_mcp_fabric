import pytest
from adaptive_mcp_fabric import DAGPlanner, PlanStep, PlanValidationError


def test_layers_schedule_independent_steps_together():
    planner = DAGPlanner()
    plan = planner.build([PlanStep("a", "s:a"), PlanStep("b", "s:b"), PlanStep("c", "s:c", depends_on=("a", "b"))])
    assert tuple(step.id for step in planner.layers(plan)[0]) == ("a", "b")
    assert tuple(step.id for step in planner.layers(plan)[1]) == ("c",)


def test_cycle_is_rejected():
    planner = DAGPlanner()
    with pytest.raises(PlanValidationError):
        planner.build([PlanStep("a", "s:a", depends_on=("b",)), PlanStep("b", "s:b", depends_on=("a",))])
