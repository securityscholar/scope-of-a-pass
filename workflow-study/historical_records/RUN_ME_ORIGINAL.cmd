@echo off
cd /d "%~dp0"
python -B reproduce.py
if errorlevel 1 (echo Reproduction failed. Review the log above.)
pause
