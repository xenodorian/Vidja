@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo   Vidja - one-click launcher
echo ========================================
echo.

REM If portable runtime is already set up, just start ComfyUI.
if exist "%~dp0ComfyUI_windows_portable\run_nvidia_gpu.bat" (
  echo Found existing portable install. Starting ComfyUI...
  echo.
  start "" "%~dp0ComfyUI_windows_portable\run_nvidia_gpu.bat"
  timeout /t 3 /nobreak >nul
  start "" "http://127.0.0.1:8188"
  exit /b 0
)

if exist "%~dp0ComfyUI_windows_portable\python_embeded\python.exe" (
  if exist "%~dp0ComfyUI_windows_portable\ComfyUI\main.py" (
    echo Found portable Python + ComfyUI. Starting...
    echo.
    start "Vidja ComfyUI" /D "%~dp0ComfyUI_windows_portable\ComfyUI" ^
      "%~dp0ComfyUI_windows_portable\python_embeded\python.exe" -s main.py --windows-standalone-build --listen 127.0.0.1 --port 8188
    timeout /t 5 /nobreak >nul
    start "" "http://127.0.0.1:8188"
    exit /b 0
  )
)

REM First run: full autonomous setup (downloads runtime, models, smoke test).
echo No portable install found yet.
echo Running full setup via Setup_Vidja_Windows.bat ...
echo This will download several GB and may take a while.
echo.
if not exist "%~dp0Setup_Vidja_Windows.bat" (
  echo ERROR: Setup_Vidja_Windows.bat is missing from this folder.
  pause
  exit /b 1
)

call "%~dp0Setup_Vidja_Windows.bat"
exit /b %ERRORLEVEL%
