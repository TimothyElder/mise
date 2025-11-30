# Makefile for Mise

# Detect OS
ifeq ($(OS),Windows_NT)
    PYTHON = python3
    VENV_PYTHON = .\.venv\Scripts\python.exe
    VENV_PIP    = .\.venv\Scripts\pip.exe
else
    PYTHON = python3
    VENV_PYTHON = .venv/bin/python
    VENV_PIP    = .venv/bin/pip
endif

PYDOC_MODULES := $(shell $(PYTHON) -c "import sys, pkgutil; sys.path.insert(0, 'src'); import mise; print(' '.join(m.name for m in pkgutil.walk_packages(mise.__path__, 'mise.') if m.name != 'mise.__main__'))")
DMG_NAME = Mise-0.1.2.dmg
APP_NAME := mise
PACKAGE := mise

.PHONY: help venv install dev run build-macos build-windows test clean distclean docs

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

install:
	$(PYTHON) -m venv .venv
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install pyinstaller
	$(VENV_PIP) install -e .

run: install
	$(PY) -m $(PACKAGE)

dev: install
	./scripts/dev-macos.sh

build-macos: install
	./scripts/build-macos.sh

build-windows: install
	$(VENV_PYTHON) -m PyInstaller mise.spec

test: install
	$(PY) -m pytest

docs:
	PYTHONPATH=src $(PYTHON) -m pydoc -w $(PYDOC_MODULES)
	mkdir -p docs
	mv -f *.html docs/

dmg: build-macos
	mkdir -p build/dmg
	cp -R dist/Mise.app build/dmg/
	hdiutil create \
	  -volname "Mise" \
	  -srcfolder build/dmg \
	  -ov \
	  -format UDZO \
	  -size 1024m \
	  dist/$(DMG_NAME)

clean:
	rm -rf build dist
	find . -name "__pycache__" -type d -exec rm -rf {} +

distclean: clean
	rm -rf $(VENV)