from adaptive_mcp_fabric import ProgressiveDiscovery, RiskLevel, ToolRegistry


class FakeClient:
    def list_tools(self, *, cursor=None):
        if cursor is None:
            return {"tools": [{"name": "read_file", "description": "read a file", "inputSchema": {"type": "object"}, "annotations": {"readOnlyHint": True}}, {"name": "delete_file", "description": "delete a file", "annotations": {"readOnlyHint": False, "destructiveHint": True}}]}
        raise AssertionError("unexpected cursor")


def test_discovery_normalizes_tool_annotations():
    registry = ToolRegistry()
    tools = ProgressiveDiscovery(registry).ingest("files", FakeClient())
    assert len(tools) == 2
    assert registry.get("files:read_file").risk is RiskLevel.LOW
    assert registry.get("files:delete_file").risk is RiskLevel.HIGH
