from adaptive_mcp_fabric import AdaptiveRouter, ToolCapability, ToolRegistry

registry = ToolRegistry()
registry.register_many([ToolCapability(server_id="weather", name="forecast", description="Get weather forecasts, rain, temperature and wind by city", tags=frozenset({"weather", "forecast"})), ToolCapability(server_id="math", name="matrix_inverse", description="Invert a square numerical matrix", tags=frozenset({"math", "linear-algebra"})), ToolCapability(server_id="search", name="web_search", description="Search public web pages for current information", tags=frozenset({"search", "web"}))])

decision = AdaptiveRouter(registry).route("Will it rain tomorrow?", top_k=2)
for candidate in decision.selected:
    print(candidate.tool.key, f"score={candidate.score:.3f}", f"semantic={candidate.semantic_score:.3f}")
