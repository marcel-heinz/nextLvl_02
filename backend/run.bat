@echo off
echo Starting nxtLvl Backend Server...
cd /d "%~dp0"
venv\Scripts\activate && python start_server.py
pause

