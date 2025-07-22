.PHONY: help install install-dev test test-coverage lint format type-check clean build docs

help:
	@echo "Available commands:"
	@echo "  make install       Install dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo "  make test          Run tests"
	@echo "  make test-coverage Run tests with coverage"
	@echo "  make lint          Run linting"
	@echo "  make format        Format code"
	@echo "  make type-check    Run type checking"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build distribution"
	@echo "  make docs          Build documentation"

install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

test:
	pytest -v

test-coverage:
	pytest -v --cov=ai --cov-report=html --cov-report=term

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

test-e2e:
	pytest -v -m e2e

benchmark:
	pytest tests/benchmarks/ -v --benchmark-only

lint:
	ruff check ai/
	black --check ai/
	mypy ai/

format:
	black ai/
	isort ai/
	ruff check --fix ai/

type-check:
	mypy ai/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

docs:
	cd docs && make html

serve-docs:
	cd docs/_build/html && python -m http.server

run:
	python -m ai.cli

run-async:
	python -m AI.Modes.async_interactive