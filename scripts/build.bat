@echo off
REM Build script for SEMP Workflow Automation
REM Usage:
REM   build.bat                              (uses examples\templates)
REM   build.bat --templates-dir my-templates (custom templates dir)

echo [1/2] Installing package ...
pip install -e .
if errorlevel 1 (
    echo ERROR: pip install failed
    exit /b 1
)

echo.
echo [2/2] Building zip ...
python scripts\build.py %*
if errorlevel 1 (
    echo ERROR: build failed
    exit /b 1
)
