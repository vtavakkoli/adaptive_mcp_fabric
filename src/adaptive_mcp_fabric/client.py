"""Minimal MCP 2026-07-28 stateless HTTP client."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from itertools import count
from typing import Any, Mapping


class MCPProtocolError(RuntimeError):
    pass


@dataclass(slots=True)
class MCPHttpClient:
    endpoint: str
    protocol_version: str = "2026-07-28"
    client_name: str = "adaptive-mcp-fabric"
    client_version: str = "0.1.0"
    timeout_s: float = 30.0
    _ids: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._ids = count(1)

    def _headers(self, method: str, name: str | None = None) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json", "MCP-Protocol-Version": self.protocol_version, "Mcp-Method": method}
        if name:
            headers["Mcp-Name"] = name
        return headers

    def call(self, method: str, params: Mapping[str, Any] | None = None, *, name: str | None = None) -> Any:
        request_id = next(self._ids)
        body = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": dict(params or {})}
        body["params"]["_meta"] = {"io.modelcontextprotocol/clientInfo": {"name": self.client_name, "version": self.client_version}}
        request = urllib.request.Request(self.endpoint, data=json.dumps(body).encode("utf-8"), headers=self._headers(method, name), method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise MCPProtocolError(f"MCP request failed: {exc}") from exc
        if payload.get("id") != request_id:
            raise MCPProtocolError("MCP response id does not match request")
        if "error" in payload:
            raise MCPProtocolError(f"MCP error: {payload['error']}")
        if "result" not in payload:
            raise MCPProtocolError("MCP response is missing result")
        return payload["result"]

    def discover(self) -> Any:
        return self.call("server/discover")

    def list_tools(self, *, cursor: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if cursor is not None:
            params["cursor"] = cursor
        return self.call("tools/list", params)

    def call_tool(self, name: str, arguments: Mapping[str, Any]) -> Any:
        return self.call("tools/call", {"name": name, "arguments": dict(arguments)}, name=name)
