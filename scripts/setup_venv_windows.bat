@echo off
REM Create a virtual environment and install requirements on Windows
python -m venv .venv
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
echo Virtual environment setup complete. To activate it later, run:
echo    call .venv\Scripts\activate.bat
