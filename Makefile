run:
	uv run fastapi dev src/main.py

install:
	uv sync --no-frozen
	uv pip compile pyproject.toml -o requirements.txt

.PHONY: format  # Format the code
format:
	uv run ruff format
	uv run ruff check --fix


.PHONY: lint  # Lint the code
lint:
	uv run ruff check
	uv run ruff format --check --diff