@echo off
chcp 65001 >nul
cd /d "%~dp0"
call .\.venv\Scripts\python.exe -m simon.main %*
if errorlevel 1 pause
