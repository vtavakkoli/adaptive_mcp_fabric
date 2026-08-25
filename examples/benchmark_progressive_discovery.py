import time
from adaptive_mcp_fabric import build_router_for_catalog


def run():
    for size in (10, 50, 100, 250, 500):
        router = build_router_for_catalog(size)
        started = time.perf_counter()
        decision = router.route("weather forecast temperature", top_k=5)
        elapsed_ms = (time.perf_counter() - started) * 1000
        print(f"catalog={size:>3} top_k={len(decision.selected)} route_ms={elapsed_ms:7.3f} first={decision.selected[0].tool.key}")


if __name__ == "__main__":
    run()
