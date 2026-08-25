"""Progressive MCP capability discovery and normalization."""

from collections.abc import Iterable
from typing import Any, Mapping, Protocol

from .models import RiskLevel, ToolCapability
from .registry import ToolRegistry


class ToolListClient(Protocol):
    def list_tools(self, *, cursor: str | None = None) -> Any: ...


def _risk_from_annotations(tool: Mapping[str, Any]) -> tuple[RiskLevel, bool]:
    annotations = tool.get("annotations") or {}
    read_only = bool(annotations.get("readOnlyHint", True))
    destructive = bool(annotations.get("destructiveHint", False))
    if destructive:
        return RiskLevel.HIGH, read_only
    if not read_only:
        return RiskLevel.MEDIUM, read_only
    return RiskLevel.LOW, read_only


class ProgressiveDiscovery:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def ingest(self, server_id: str, client: ToolListClient, *, max_pages: int = 100, default_tags: Iterable[str] = ()) -> tuple[ToolCapability, ...]:
        cursor = None
        discovered = []
        tags = frozenset(default_tags)
        for _ in range(max_pages):
            result = client.list_tools(cursor=cursor)
            if not isinstance(result, Mapping):
                raise TypeError("tools/list result must be an object")
            for raw in result.get("tools", ()):
                if not isinstance(raw, Mapping):
                    continue
                risk, read_only = _risk_from_annotations(raw)
                capability = ToolCapability(server_id=server_id, name=str(raw.get("name", "")), description=str(raw.get("description", "")), input_schema=raw.get("inputSchema") or {}, tags=tags, risk=risk, read_only=read_only, metadata={"title": raw.get("title")} if raw.get("title") else {})
                if capability.name:
                    self.registry.register(capability)
                    discovered.append(capability)
            cursor = result.get("nextCursor")
            if not cursor:
                break
        else:
            raise RuntimeError(f"tools/list exceeded max_pages={max_pages}")
        return tuple(discovered)
