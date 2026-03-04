.PHONY: help install install-dev test lint format type-check clean build

help:
	@echo "Available commands:"
	@echo "  make install       Install dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linting"
	@echo "  make format        Format code"
	@echo "  make type-check    Run type checking"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build distribution"

install:
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check ask/
	black --check ask/
	mypy ask/

format:
	black ask/
	isort ask/
	ruff check --fix ask/

type-check:
	mypy ask/

clean:
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build
