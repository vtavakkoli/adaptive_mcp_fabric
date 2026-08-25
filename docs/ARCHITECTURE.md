# Architecture

Adaptive MCP Fabric separates **protocol transport** from **tool intelligence**.

```text
User / Agent
    |
    v
AdaptiveRouter  <---- TelemetryStore
    |                    ^
    | top-k              | success + latency
    v                    |
PolicyEngine ----> DAGPlanner ----> FabricExecutor
    |                                  |
    v                                  v
ToolRegistry <---- ProgressiveDiscovery ---- MCP servers
```

## Normalized registry

`ToolRegistry` stores transport-independent `ToolCapability` records. Routing does not depend on a particular MCP SDK, model provider, vector database, or agent framework.

## Progressive discovery

`ProgressiveDiscovery` ingests `tools/list` pages and exposes a small top-k surface to the model instead of the entire catalog.

## Adaptive routing

The default score is:

```text
0.58 * semantic_relevance
+ 0.22 * observed_reliability
- 0.08 * latency_penalty
- 0.04 * token_overhead_penalty
- 0.08 * risk_penalty
```

Weights and the semantic scorer are pluggable.

## Trust and policy

Policy runs during routing and again before execution. Read-only tools are allowed by default, side-effecting/high-risk tools require confirmation, and critical-risk tools are denied.

## DAG orchestration

`DAGPlanner` validates dependencies and cycles deterministically. `FabricExecutor` runs independent nodes concurrently and propagates dependency failures.

## Transport

`MCPHttpClient` targets the stateless MCP `2026-07-28` request model while the rest of the library remains transport-independent.
