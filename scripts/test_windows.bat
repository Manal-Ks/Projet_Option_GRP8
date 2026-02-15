@echo off
REM Activate venv if present and run tests via python -m pytest
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python -m pytest -q %*
