from adaptive_mcp_fabric import MCPHttpClient


def test_mcp_2026_headers_are_routable():
    client = MCPHttpClient("http://localhost:9999/mcp")
    headers = client._headers("tools/call", "search")
    assert headers["MCP-Protocol-Version"] == "2026-07-28"
    assert headers["Mcp-Method"] == "tools/call"
    assert headers["Mcp-Name"] == "search"
