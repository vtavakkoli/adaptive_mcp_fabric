import asyncio
from adaptive_mcp_fabric import DAGPlanner, FabricExecutor, PlanStep, RiskLevel, ToolCapability, ToolRegistry


async def main():
    registry = ToolRegistry()
    registry.register(ToolCapability(server_id="files", name="delete_file", description="Delete a local file", tags=frozenset({"files", "write"}), risk=RiskLevel.HIGH, read_only=False))
    async def invoke(server_id, tool_name, arguments):
        return {"server": server_id, "tool": tool_name, "arguments": arguments}
    async def confirm(step, reason):
        print(f"approval requested for {step.id}: {reason}")
        return True
    plan = DAGPlanner().build([PlanStep("delete-temp", "files:delete_file", {"path": "/tmp/example.txt"})])
    print(await FabricExecutor(registry, invoke).execute(plan, confirm=confirm))


if __name__ == "__main__":
    asyncio.run(main())
