.PHONY: test lint lint-fix clean

# Run all tests
test:
	pytest -vv --maxfail=1 --disable-warnings

# Check formatting, linting, types
lint:
	ruff format --check pii/
	ruff check pii/
	mypy pii/

# Auto-fix formatting and lint issues
lint-fix:
	ruff format pii/
	ruff check --fix pii/

# Clean caches
clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
