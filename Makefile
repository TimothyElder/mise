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

# Linux variables
DEB_VERSION = 0.1.2
DEB_ARCH = amd64
APP_DESCRIPTION = Qualitative data analysis tool for social scientists

.PHONY: help venv install dev run build-macos build-windows build-linux build-deb test clean distclean docs

help:
	@echo "Common targets:"
	@echo "  make venv         - create virtualenv in .venv"
	@echo "  make install      - install Mise (editable) and deps into .venv"
	@echo "  make run          - run Mise from source (GUI)"
	@echo "  make dev          - run dev script for macOS"
	@echo "  make build-macos  - build macOS app (wraps scripts/build-macos.sh)"
	@echo "  make build-windows- build Windows app (wraps scripts/build-windows.bat)"
	@echo "  make build-linux  - build Linux executable"
	@echo "  make build-deb    - build Debian/Ubuntu .deb package"
	@echo "  make dmg          - create macOS DMG installer"
	@echo "  make test         - run tests (if/when you add them)"
	@echo "  make clean        - remove build artifacts"
	@echo "  make distclean    - clean + remove .venv"

$(VENV):
	$(PYTHON) -m venv $(VENV)

venv: $(VENV)

install:
	$(PYTHON) -m venv .venv
	$(VENV_PIP) install pyinstaller
	$(VENV_PIP) install -e .

run: install
	$(PY) -m $(PACKAGE)

dev: install
	./scripts/dev-macos.sh

build-macos: install
	./scripts/build-macos.sh

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

build-windows: install
	$(VENV_PYTHON) -m PyInstaller mise.spec

build-linux: install
	$(VENV_PYTHON) -m PyInstaller mise.spec
	@echo "Linux executable built in dist/Mise"

build-deb: build-linux
	@command -v dpkg-deb >/dev/null 2>&1 || { echo "Error: dpkg-deb not found. Install with: sudo apt-get install dpkg"; exit 1; }
	@echo "Building .deb package..."
	mkdir -p build/deb/DEBIAN
	mkdir -p build/deb/usr/bin
	mkdir -p build/deb/usr/share/applications
	mkdir -p build/deb/usr/share/icons/hicolor/256x256/apps
	mkdir -p build/deb/usr/share/doc/mise
	
	# Copy executable
	cp dist/Mise build/deb/usr/bin/mise
	chmod 755 build/deb/usr/bin/mise
	
	# Copy icon
	cp src/mise/assets/mise-icon.png build/deb/usr/share/icons/hicolor/256x256/apps/mise.png
	
	# Create .desktop file
	@echo "[Desktop Entry]" > build/deb/usr/share/applications/mise.desktop
	@echo "Name=Mise" >> build/deb/usr/share/applications/mise.desktop
	@echo "Comment=$(APP_DESCRIPTION)" >> build/deb/usr/share/applications/mise.desktop
	@echo "Exec=/usr/bin/mise" >> build/deb/usr/share/applications/mise.desktop
	@echo "Icon=mise" >> build/deb/usr/share/applications/mise.desktop
	@echo "Terminal=false" >> build/deb/usr/share/applications/mise.desktop
	@echo "Type=Application" >> build/deb/usr/share/applications/mise.desktop
	@echo "Categories=Education;Science;" >> build/deb/usr/share/applications/mise.desktop
	
	# Create control file
	@echo "Package: mise" > build/deb/DEBIAN/control
	@echo "Version: $(DEB_VERSION)" >> build/deb/DEBIAN/control
	@echo "Section: science" >> build/deb/DEBIAN/control
	@echo "Priority: optional" >> build/deb/DEBIAN/control
	@echo "Architecture: $(DEB_ARCH)" >> build/deb/DEBIAN/control
	@echo "Maintainer: Timothy Elder <timothy.b.elder@dartmouth.edu>" >> build/deb/DEBIAN/control
	@echo "Description: $(APP_DESCRIPTION)" >> build/deb/DEBIAN/control
	@echo " Mise is a GUI application for qualitative data analysis" >> build/deb/DEBIAN/control
	@echo " designed for social scientists." >> build/deb/DEBIAN/control
	
	# Create copyright file
	@echo "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/" > build/deb/usr/share/doc/mise/copyright
	@echo "Upstream-Name: Mise" >> build/deb/usr/share/doc/mise/copyright
	@echo "Source: https://github.com/TimothyElder/mise" >> build/deb/usr/share/doc/mise/copyright
	@echo "" >> build/deb/usr/share/doc/mise/copyright
	@echo "Files: *" >> build/deb/usr/share/doc/mise/copyright
	@echo "Copyright: 2025 Mímir Research" >> build/deb/usr/share/doc/mise/copyright
	@echo "License: GPL-3+" >> build/deb/usr/share/doc/mise/copyright
	@echo "" >> build/deb/usr/share/doc/mise/copyright
	@echo "License: GPL-3+" >> build/deb/usr/share/doc/mise/copyright
	@echo " This program is free software: you can redistribute it and/or modify" >> build/deb/usr/share/doc/mise/copyright
	@echo " it under the terms of the GNU General Public License as published by" >> build/deb/usr/share/doc/mise/copyright
	@echo " the Free Software Foundation, either version 3 of the License, or" >> build/deb/usr/share/doc/mise/copyright
	@echo " (at your option) any later version." >> build/deb/usr/share/doc/mise/copyright
	@echo " ." >> build/deb/usr/share/doc/mise/copyright
	@echo " This program is distributed in the hope that it will be useful," >> build/deb/usr/share/doc/mise/copyright
	@echo " but WITHOUT ANY WARRANTY; without even the implied warranty of" >> build/deb/usr/share/doc/mise/copyright
	@echo " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the" >> build/deb/usr/share/doc/mise/copyright
	@echo " GNU General Public License for more details." >> build/deb/usr/share/doc/mise/copyright
	@echo " ." >> build/deb/usr/share/doc/mise/copyright
	@echo " On Debian systems, the complete text of the GNU General" >> build/deb/usr/share/doc/mise/copyright
	@echo " Public License version 3 can be found in" >> build/deb/usr/share/doc/mise/copyright
	@echo " \"/usr/share/common-licenses/GPL-3\"." >> build/deb/usr/share/doc/mise/copyright
	
	dpkg-deb --build build/deb dist/mise_$(DEB_VERSION)_$(DEB_ARCH).deb
	@echo "✓ Debian package created: dist/mise_$(DEB_VERSION)_$(DEB_ARCH).deb"

test:
	$(PY) -m pytest

release-macos: clean build-macos dmg
	@echo "✓ macOS release built: dist/$(DMG_NAME)"
	@echo "Ready to tag release"

release-windows: clean build-windows
	@echo "✓ Windows release built: dist/Mise.exe"
	@echo "Ready to tag release"

release-linux: clean build-linux build-deb
	@echo "✓ Linux release built: dist/mise_$(DEB_VERSION)_$(DEB_ARCH).deb"
	@echo "Ready to tag release"

docs:
	PYTHONPATH=src $(PYTHON) -m pydoc -w $(PYDOC_MODULES)
	mkdir -p docs
	mv -f *.html docs/

clean:
	rm -rf build dist
	find . -name "__pycache__" -type d -exec rm -rf {} +

distclean: clean
	rm -rf $(VENV)