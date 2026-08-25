.PHONY: install test lint check demo benchmark

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	python -m ruff check src tests examples

check: lint test

demo:
	python examples/quickstart.py

benchmark:
	python examples/benchmark_progressive_discovery.py
