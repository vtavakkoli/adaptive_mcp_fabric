# Adaptive MCP Fabric

**Progressive discovery, trust-aware routing, and concurrent orchestration for large Model Context Protocol tool ecosystems.**

[![CI](https://github.com/vtavakkoli/mcp-test/actions/workflows/ci.yml/badge.svg)](https://github.com/vtavakkoli/mcp-test/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-2026--07--28-111827)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Adaptive MCP Fabric turns the original `mcp-test` experiment into a reusable, framework-independent Python library for agents that must operate across **large, heterogeneous MCP catalogs** without dumping every tool schema into the model.

> **Discover broadly, expose narrowly, execute safely, and learn from runtime evidence.**

## Why this exists

A production agent may connect to tens of servers and hundreds of tools. Sending the complete catalog increases context cost and can make tool selection harder. Adaptive MCP Fabric introduces a control plane between the agent and MCP servers.

```text
                         Agent / LLM
                              |
                              v
                   +----------------------+
                   | Adaptive MCP Fabric  |
                   +----------------------+
                    |     |      |      |
              discovery routing policy planner
                    \     |      |     /
                     v    v      v    v
                    Top-K MCP capabilities
                              |
                 +------------+------------+
                 |            |            |
              Search        Files        GitHub  ...
                MCP           MCP          MCP
```

## Core capabilities

- **Progressive discovery** — normalize paginated `tools/list` catalogs and reveal only top-k tools.
- **Adaptive routing** — blend relevance, reliability, latency, token overhead, and risk.
- **Trust-aware policy** — allow/confirm/deny gates with conservative side-effect defaults.
- **DAG execution** — validate dependencies and run independent steps concurrently.
- **Runtime adaptation** — update reliability and latency from actual executions.
- **MCP 2026 foundation** — stateless HTTP adapter with `MCP-Protocol-Version`, `Mcp-Method`, `Mcp-Name`, `server/discover`, `tools/list`, and `tools/call`.

## Install

```bash
git clone https://github.com/vtavakkoli/mcp-test.git
cd mcp-test
python -m pip install -e ".[dev]"
```

The core library has **zero runtime Python dependencies**.

## 30-second example

```python
from adaptive_mcp_fabric import AdaptiveRouter, ToolCapability, ToolRegistry

registry = ToolRegistry()
registry.register_many([
    ToolCapability(server_id="weather", name="forecast", description="Weather forecast, rain, temperature and wind by city", tags=frozenset({"weather", "forecast"})),
    ToolCapability(server_id="math", name="matrix_inverse", description="Invert a square numerical matrix", tags=frozenset({"math", "linear-algebra"})),
])

decision = AdaptiveRouter(registry).route("Will it rain tomorrow?", top_k=1)
print(decision.selected[0].tool.key)
# weather:forecast
```

Run with:

```bash
python examples/quickstart.py
```

or:

```bash
docker compose run --rm fabric-demo
```

## Architecture

| Layer | Responsibility |
|---|---|
| `ToolRegistry` | Normalized cross-server capability catalog |
| `ProgressiveDiscovery` | MCP `tools/list` ingestion and pagination |
| `AdaptiveRouter` | Top-k multi-objective ranking |
| `PolicyEngine` | Trust/risk/scoped authorization decisions |
| `TelemetryStore` | Reliability and latency evidence |
| `DAGPlanner` | Plan validation and concurrency layers |
| `FabricExecutor` | Policy-gated execution |
| `MCPHttpClient` | Stateless MCP HTTP transport |
| `AdaptiveMCPFabric` | High-level facade |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## MCPBench

```bash
python examples/benchmark_progressive_discovery.py
```

or:

```bash
docker compose --profile benchmark run --rm fabric-benchmark
```

See [docs/BENCHMARK.md](docs/BENCHMARK.md) for the research roadmap.

## Quality gate

```bash
make check
```

CI tests Python 3.11, 3.12, and 3.13.

## Legacy demo

The original Node.js/Ollama/SearXNG + matrix/Hanoi demonstration is retained for reproducibility but is no longer the primary architecture.

```bash
docker compose --profile legacy up --build
```

## Roadmap

- official MCP SDK adapters;
- embedding and cross-encoder rankers;
- persistent/vector capability registries;
- server-card discovery;
- Tasks extension support for durable work;
- workload identity and delegated authorization;
- OPA/Cedar policy backends;
- OpenTelemetry export;
- MCPBench datasets with adversarial/overlapping tool catalogs;
- learned routing policies.

## Status

`0.1.0` is an **alpha research/library foundation**.

## License

MIT License. See [LICENSE](LICENSE).

## Author

**Dr. Vahid Tavakkoli**
