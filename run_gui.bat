@echo off
cd /d %~dp0
python gui.py
if errorlevel 1 (
  echo.
  echo If drag-and-drop support is missing, install it with:
  echo pip install tkinterdnd2
)
pause
