#!/usr/bin/env bash
set -e

# Ensure we're in project root
cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
    echo "Error: .venv not found. Run 'make install' first."
    exit 1
fi

source .venv/bin/activate

# Ensure pyinstaller is available
pip show pyinstaller >/dev/null 2>&1 || pip install pyinstaller

# Clean old builds
rm -rf build dist

# Build from spec
pyinstaller mise.spec