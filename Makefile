.PHONY: lint test coverage typecheck verify

lint:
	prek run

typecheck:
	uv run ty check

test:
	uv run pytest

coverage:
	uv run coverage run -m pytest
	uv run coverage report -m

verify:
	uv sync --all-extras --group dev --locked
	prek run --all-files
	uv run pytest --cov=weatherflow4py --cov-branch --cov-report=term-missing
