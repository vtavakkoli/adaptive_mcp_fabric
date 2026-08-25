"""Tool capability registry."""

from collections.abc import Iterable

from .models import ToolCapability


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolCapability] = {}

    def register(self, tool: ToolCapability) -> None:
        self._tools[tool.key] = tool

    def register_many(self, tools: Iterable[ToolCapability]) -> None:
        for tool in tools:
            self.register(tool)

    def unregister(self, tool_key: str) -> None:
        self._tools.pop(tool_key, None)

    def get(self, tool_key: str) -> ToolCapability:
        try:
            return self._tools[tool_key]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {tool_key}") from exc

    def all(self) -> tuple[ToolCapability, ...]:
        return tuple(self._tools[key] for key in sorted(self._tools))

    def by_server(self, server_id: str) -> tuple[ToolCapability, ...]:
        return tuple(tool for tool in self.all() if tool.server_id == server_id)

    def __len__(self) -> int:
        return len(self._tools)
