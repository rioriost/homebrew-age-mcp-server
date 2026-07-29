SHELL := /bin/sh

REPO_ROOT := $(CURDIR)
UV ?= uv
PYTHON ?= python3

DIST_DIR := $(REPO_ROOT)/dist
FORMULA_DIR := $(REPO_ROOT)/Formula
FORMULA_FILE := $(FORMULA_DIR)/age_mcp_server.rb

.PHONY: release-artifacts sync check lint test integration security build formula

release-artifacts: sync build formula

sync:
	$(UV) sync --extra test --extra telemetry --group dev

check: lint test security build

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

test:
	$(UV) run pytest \
		--cov=age_mcp_server \
		--cov-report=term-missing \
		--cov-fail-under=80

integration:
	$(UV) run pytest -m integration tests/integration

security:
	$(UV) audit --locked --preview-features audit-command
	$(UV) run bandit -q -r src

build:
	rm -rf "$(DIST_DIR)"
	$(UV) build
	$(UV) run twine check "$(DIST_DIR)"/*

formula:
	mkdir -p "$(FORMULA_DIR)"
	genformula \
		--pyproject "$(REPO_ROOT)/pyproject.toml" \
		--install-mode advanced \
		--source-subdir . \
		--output "$(FORMULA_FILE)"
