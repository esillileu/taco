.PHONY: check format lint test validate-docs

check: validate-docs

format:
	uv run --extra dev ruff format .

lint:
	uv run --extra dev ruff check .

test:
	uv run --extra dev pytest

validate-docs:
	uv run --extra dev python scripts/validate_docs.py
