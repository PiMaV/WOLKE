@echo off
REM Build WOLKE.exe with PyInstaller. Run from repo root: scripts\build_exe.bat
REM Requires: uv (https://docs.astral.sh/uv/)
cd /d "%~dp0.."
if not exist "wolke\__init__.py" (
  echo Error: Run from repo root. wolke package not found.
  exit /b 1
)
uv sync --extra dev
uv run pyinstaller wolke.spec
echo.
echo If successful: dist\WOLKE.exe
echo Run it; browser will open. config.ini must be next to the EXE or set WOLKE_CONFIG.
