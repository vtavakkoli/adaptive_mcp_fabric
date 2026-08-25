from adaptive_mcp_fabric import AdaptiveRouter, RiskLevel, TelemetryStore, ToolCapability, ToolRegistry


def _tool(name: str, description: str, **kwargs):
    return ToolCapability(server_id="demo", name=name, description=description, **kwargs)


def test_router_selects_relevant_weather_tool():
    registry = ToolRegistry()
    registry.register_many([_tool("matrix_inverse", "invert square numerical matrices"), _tool("weather_forecast", "weather forecast temperature rain and wind"), _tool("search_web", "search public web pages")])
    decision = AdaptiveRouter(registry).route("weather forecast and rain", top_k=1)
    assert decision.selected[0].tool.name == "weather_forecast"


def test_router_filters_critical_risk():
    registry = ToolRegistry()
    registry.register(_tool("destroy_everything", "weather forecast but destructive", risk=RiskLevel.CRITICAL, read_only=False))
    decision = AdaptiveRouter(registry).route("weather forecast", top_k=5)
    assert decision.selected == ()
    assert decision.rejected_by_policy == 1


def test_telemetry_reliability_changes_ranking():
    registry = ToolRegistry()
    a = _tool("search_primary", "search documents")
    b = _tool("search_backup", "search documents")
    registry.register_many([a, b])
    telemetry = TelemetryStore(smoothing=1.0)
    for _ in range(4):
        telemetry.record(a.key, ok=False, latency_ms=100)
        telemetry.record(b.key, ok=True, latency_ms=100)
    decision = AdaptiveRouter(registry, telemetry=telemetry).route("search documents", top_k=2)
    assert decision.selected[0].tool.key == b.key
