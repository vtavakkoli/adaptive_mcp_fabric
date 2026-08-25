# MCPBench direction

The included synthetic benchmark is the foundation for a larger progressive-discovery evaluation.

## Research questions

1. How does top-k accuracy change from 10 to 1,000+ tools?
2. How much context overhead is avoided by progressive discovery?
3. Can a smaller model with adaptive routing match a larger model receiving the full catalog?
4. How much do reliability, latency, and risk signals improve semantic-only routing?
5. What is the effect of stale or adversarial tool descriptions?

## Baselines

- all tools exposed;
- keyword/BM25 routing;
- embedding top-k;
- LLM router;
- Adaptive MCP Fabric.

## Metrics

Top-1 accuracy, top-k recall, task success, unsafe-tool selection, exposed schema tokens, routing latency, end-to-end latency, retries, and cost per successful task.

```bash
docker compose --profile benchmark run --rm fabric-benchmark
```
