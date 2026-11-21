VENV := .venv
PY   := $(VENV)/bin/python

.PHONY: help install run-cli test watch lint lint-fix format format-check check clean
.DEFAULT_GOAL := help

help: ## list commands
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

$(VENV)/.installed: requirements-dev.txt
	python3 -m venv $(VENV)
	$(PY) -m pip install -r requirements-dev.txt
	@touch $@

install: $(VENV)/.installed ## create venv and install dev tools

lint: install ## ruff check (read-only)
	$(VENV)/bin/ruff check .

lint-fix: install ## ruff check with autofix
	$(VENV)/bin/ruff check --fix .

format: install ## ruff format (rewrites files)
	$(VENV)/bin/ruff format .

format-check: install ## ruff format check (read-only)
	$(VENV)/bin/ruff format --check .

clean: ## delete venv and caches
	rm -rf $(VENV) .ruff_cache .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

test: install ## run tests once
	$(PY) -m pytest

run-cli: install ## run the terminal mode
	$(PY) main.py cli

watch: install ## re-run tests on save
	$(VENV)/bin/ptw --now --clear --patterns '**/*.py' --ignore-patterns '**/.venv/**' $(CURDIR)

check: lint format-check test ## pre-commit gate: lint + format check + tests
