VENV := .venv
PY   := $(VENV)/bin/python

.PHONY: help install lint format clean
.DEFAULT_GOAL := help

help: ## list commands
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

$(VENV)/.installed: requirements-dev.txt
	python3 -m venv $(VENV)
	$(PY) -m pip install -r requirements-dev.txt
	@touch $@

install: $(VENV)/.installed ## create venv and install dev tools

lint: install ## ruff check with autofix
	$(VENV)/bin/ruff check --fix .

format: install ## ruff format
	$(VENV)/bin/ruff format .

clean: ## delete venv and caches
	rm -rf $(VENV) .ruff_cache .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

test: install ## run tests once
	$(PY) -m pytest
	
watch: install ## re-run tests on save
	$(VENV)/bin/ptw .