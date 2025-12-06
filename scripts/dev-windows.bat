@echo off
IF NOT EXIST .venv (
    python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install -e ".[dev]"

mise