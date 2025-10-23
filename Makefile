.PHONY: help install install-dev format lint type-check security test clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

format: ## Format code with black and isort
	black .
	isort .

lint: ## Run linting with ruff
	ruff check . --fix

type-check: ## Run type checking with mypy
	mypy .

security: ## Run security checks with bandit and safety
	bandit -r . -f json -o bandit-report.json
	safety check

test: ## Run tests with pytest
	pytest --cov=. --cov-report=html --cov-report=term-missing

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -f bandit-report.json

all-checks: format lint type-check security test ## Run all checks

ci: install-dev all-checks ## Run CI pipeline locally
