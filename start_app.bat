@echo off
cd /d "%~dp0"
call conda activate vb311
uvicorn main:app --reload < nul

@REM call python main.py
