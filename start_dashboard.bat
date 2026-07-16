@echo off
setlocal EnableExtensions
cd /d "%~dp0"

call :find_python
if errorlevel 1 goto :python_error

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating local Python environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

echo [2/3] Installing dashboard dependencies...
if exist "offline_packages\" (
    echo Using local offline_packages folder.
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --no-index --find-links offline_packages -r requirements.txt
) else (
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
)
if errorlevel 1 goto :dependency_error

echo [3/3] Starting AI Operations Report...
echo Open http://localhost:8501 if the browser does not open automatically.
start "" http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
goto :end

:find_python
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=py -3"
        exit /b 0
    )
)
where python >nul 2>nul
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=python"
        exit /b 0
    )
)
exit /b 1

:python_error
echo.
echo Python 3.10 or newer was not found.
echo Install 64-bit Python first and enable "Add Python to PATH".
pause
goto :end

:dependency_error
echo.
echo Dependency installation failed.
echo For a computer without internet, copy the offline_packages folder created by prepare_offline_package.bat.
pause
goto :end

:error
echo.
echo Dashboard startup failed. Review the message above.
pause

:end
endlocal
