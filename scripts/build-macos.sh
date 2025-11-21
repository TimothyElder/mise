#!/usr/bin/env bash
set -e
source .venv/bin/activate
pyinstaller \
    --name "Mise" \
    --windowed \
    --noconfirm \
    --clean \
    src/mise/__main__.py