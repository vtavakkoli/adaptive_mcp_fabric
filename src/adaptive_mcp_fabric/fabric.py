"""High-level facade for Adaptive MCP Fabric."""

from __future__ import annotations

import asyncio
from typing import Any, Mapping

from .client import MCPHttpClient
from .discovery import ProgressiveDiscovery
from .models import ExecutionContext, RouteDecision
from .policy import PolicyEngine
from .registry import ToolRegistry
from .router import AdaptiveRouter
from .telemetry import TelemetryStore


class AdaptiveMCPFabric:
    def __init__(self, *, policy: PolicyEngine | None = None) -> None:
        self.registry = ToolRegistry()
        self.telemetry = TelemetryStore()
        self.policy = policy or PolicyEngine()
        self.router = AdaptiveRouter(self.registry, telemetry=self.telemetry, policy=self.policy)
        self.discovery = ProgressiveDiscovery(self.registry)
        self._clients: dict[str, MCPHttpClient] = {}

    def add_http_server(self, server_id: str, endpoint: str, *, discover_tools: bool = True, tags: tuple[str, ...] = ()) -> MCPHttpClient:
        if server_id in self._clients:
            raise ValueError(f"server already registered: {server_id}")
        client = MCPHttpClient(endpoint)
        self._clients[server_id] = client
        if discover_tools:
            self.discovery.ingest(server_id, client, default_tags=tags)
        return client

    def route(self, query: str, *, top_k: int = 5, context: ExecutionContext | None = None) -> RouteDecision:
        return self.router.route(query, top_k=top_k, context=context)

    async def invoke(self, server_id: str, tool_name: str, arguments: Mapping[str, Any]) -> Any:
        try:
            client = self._clients[server_id]
        except KeyError as exc:
            raise KeyError(f"unknown MCP server: {server_id}") from exc
        return await asyncio.to_thread(client.call_tool, tool_name, arguments)
