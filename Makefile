# Developer commands. Run inside an activated virtual environment (see README).
# Every target calls `python -m <tool>`, so the same file works on Windows and in CI.

PYTHON ?= python

.PHONY: install lint typecheck test check

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy

test:
	$(PYTHON) -m pytest

check: lint typecheck test
