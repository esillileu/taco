.PHONY: check format lint test validate-docs

check: validate-docs

format:
	ruff format .

lint:
	ruff check .

test:
	pytest

validate-docs:
	python3 scripts/validate_docs.py
