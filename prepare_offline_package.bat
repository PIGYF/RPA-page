@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=py -3"
) else (
    set "PYTHON=python"
)

echo Downloading Windows Python packages for offline deployment...
if not exist "offline_packages" mkdir offline_packages
%PYTHON% -m pip download --dest offline_packages -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Offline package is ready.
echo Copy this whole project folder, including offline_packages, to the target computer.
echo Do not copy .venv or .streamlit\secrets.toml.
pause
goto :end

:error
echo.
echo Could not build the offline package. Check the internet connection and Python installation.
pause

:end
endlocal
