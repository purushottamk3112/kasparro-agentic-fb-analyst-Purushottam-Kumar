.PHONY: help setup run test lint clean

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help:
	@echo "Kasparro Agentic FB Analyst - Makefile Commands"
	@echo ""
	@echo "  make setup    - Create venv and install dependencies"
	@echo "  make run      - Run analysis with default query"
	@echo "  make test     - Run unit tests"
	@echo "  make lint     - Run code quality checks"
	@echo "  make clean    - Remove generated files and cache"
	@echo "  make format   - Format code with black"
	@echo ""

setup:
	@echo "Setting up environment..."
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "Setup complete! Activate with: source $(VENV)/bin/activate"

run:
	@echo "Running analysis..."
	$(BIN)/python src/run.py "Analyze ROAS drop in last 7 days"

test:
	@echo "Running tests..."
	$(BIN)/python -m pytest tests/ -v || $(BIN)/python tests/test_evaluator.py

lint:
	@echo "Running linter..."
	-$(BIN)/pylint src/ --rcfile=.pylintrc || echo "Pylint not installed or issues found"

format:
	@echo "Formatting code..."
	-$(BIN)/black src/ tests/ || echo "Black not installed"

clean:
	@echo "Cleaning generated files..."
	rm -rf reports/*.md reports/*.json
	rm -rf logs/*.log logs/*.jsonl
	rm -rf .pytest_cache
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf *.pyc */*.pyc */*/*.pyc
	rm -rf .mypy_cache
	@echo "Clean complete!"

clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "All clean!"
