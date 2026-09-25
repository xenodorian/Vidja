@echo off
setlocal
cd /d "%~dp0"
echo Packaging the already-tested Vidja runtime...
if not exist "Vidja_Portable\ComfyUI\main.py" (
  echo ERROR: Vidja_Portable is not installed.
  echo Run Setup_Vidja_Windows.bat first.
  pause
  exit /b 1
)
if exist "_bootstrap_python\python.exe" (
  "_bootstrap_python\python.exe" -c "import zipfile,pathlib,sys; root=pathlib.Path('Vidja_Portable'); out=pathlib.Path('Vidja_ComfyUI_Ready.zip'); out.unlink(missing_ok=True); z=zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED,allowZip64=True); [z.write(p,p.relative_to(root).as_posix()) for p in root.rglob('*') if p.is_file() and 'ComfyUI\\output' not in p.as_posix()]; z.close(); print(out, out.stat().st_size)"
  if errorlevel 1 goto :fail
  echo Package created: Vidja_ComfyUI_Ready.zip
  pause
  exit /b 0
)
echo ERROR: Bootstrap Python is missing.
echo Run Setup_Vidja_Windows.bat first.
:fail
echo Packaging failed.
pause
exit /b 1
