@echo off
REM Activate venv if present and run the demo
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python demo_dev_run.py %*
