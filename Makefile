# Makefile for Mise

PYTHON ?= python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PY := $(VENV_BIN)/python

APP_NAME := mise
PACKAGE := mise

.PHONY: help venv install dev run build-macos build-windows test clean distclean

help:
	@echo "Common targets:"
	@echo "  make venv         - create virtualenv in .venv"
	@echo "  make install      - install Mise (editable) and deps into .venv"
	@echo "  make run          - run Mise from source (GUI)"
	@echo "  make dev          - run dev script for macOS"
	@echo "  make build-macos  - build macOS app (wraps scripts/build-macos.sh)"
	@echo "  make build-windows- build Windows app (wraps scripts/build-windows.bat)"
	@echo "  make test         - run tests (if/when you add them)"
	@echo "  make clean        - remove build artifacts"
	@echo "  make distclean    - clean + remove .venv"

$(VENV):
	$(PYTHON) -m venv $(VENV)

venv: $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -e .

run: install
	$(PY) -m $(PACKAGE)

dev: install
	./scripts/dev-macos.sh

build-macos: install
	./scripts/build-macos.sh

build-windows:
	./scripts/build-windows.bat

test: install
	$(PY) -m pytest

clean:
	rm -rf build dist
	find . -name "__pycache__" -type d -exec rm -rf {} +

distclean: clean
	rm -rf $(VENV)