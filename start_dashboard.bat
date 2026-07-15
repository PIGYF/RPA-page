@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON=py -3"
) else (
    set "PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

echo Installing or updating dependencies...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :error

echo Starting dashboard at http://localhost:8501
start "" http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501
goto :end

:error
echo.
echo Dashboard startup failed. Check that Python 3.10 or newer is installed.
pause

:end
endlocal
