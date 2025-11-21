@echo off
call .venv\Scripts\activate.bat
pyinstaller --name "Mise" --windowed --noconfirm --clean src\mise\__main__.py