import asyncio
from adaptive_mcp_fabric import DAGPlanner, FabricExecutor, PlanStep, ToolCapability, ToolRegistry


async def test_executor_runs_dag_and_records_results():
    registry = ToolRegistry()
    registry.register_many([ToolCapability("s", "a", "first"), ToolCapability("s", "b", "second"), ToolCapability("s", "c", "third")])
    seen = []
    async def invoke(server_id, tool_name, arguments):
        await asyncio.sleep(0)
        seen.append((server_id, tool_name, arguments))
        return {"tool": tool_name}
    plan = DAGPlanner().build([PlanStep("1", "s:a"), PlanStep("2", "s:b"), PlanStep("3", "s:c", depends_on=("1", "2"))])
    report = await FabricExecutor(registry, invoke).execute(plan)
    assert report.ok
    assert report.by_step()["3"].output == {"tool": "c"}
    assert {name for _, name, _ in seen} == {"a", "b", "c"}
