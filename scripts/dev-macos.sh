#!/usr/bin/env bash
set -e

# Create venv if needed
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

# Run app
mise

conda activate mise
cd /Users/timothyelder/Documents/mise
python -m mise