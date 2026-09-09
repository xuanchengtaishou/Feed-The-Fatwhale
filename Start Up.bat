@echo off
chcp 65001 >nul 2>&1
title Analytics System Manager

:menu
cls
echo ========================================
echo    Analytics System Manager
echo ========================================
echo.
echo   [1] Start All Services
echo   [2] Stop All Services
echo   [3] Restart All Services
echo   [4] Check Status
echo   [5] Install Dependencies
echo   [6] Clean Cache
echo   [0] Exit
echo.
echo ========================================
set /p choice="Select (0-6): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto install
if "%choice%"=="6" goto clean
if "%choice%"=="0" exit
goto menu

:start
cls
echo ========================================
echo    Starting Services...
echo ========================================
echo.

cd /d "%~dp0app"

:: Check dependencies
echo Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

:: Kill existing processes on ports
echo Cleaning ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start backend
echo Starting Backend...
start "Backend" cmd /k "title Backend && cd /d %~dp0app && echo Backend starting... && python main.py"

:: Wait
timeout /t 3 /nobreak >nul

:: Start frontend
echo Starting Frontend...
start "Frontend" cmd /k "title Frontend && cd /d %~dp0app && echo Frontend starting... && python -m streamlit run streamlit_app.py"

echo.
echo ========================================
echo    Services Started!
echo ========================================
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
pause
goto menu

:stop
cls
echo ========================================
echo    Stopping Services...
echo ========================================
echo.

taskkill /FI "WINDOWTITLE eq Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend" /F >nul 2>&1

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo All services stopped.
pause
goto menu

:restart
cls
echo ========================================
echo    Restarting Services...
echo ========================================
echo.

echo Stopping...
call :stop_silent
timeout /t 2 /nobreak >nul
echo Starting...
goto start

:stop_silent
taskkill /FI "WINDOWTITLE eq Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend" /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do (
    taskkill /F /PID %%a >nul 2>&1
)
exit /b

:status
cls
echo ========================================
echo    Service Status
echo ========================================
echo.

echo Backend (port 8000):
netstat -ano | findstr :8000 | findstr LISTENING >nul
if errorlevel 1 (
    echo    [STOPPED]
) else (
    echo    [RUNNING]
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        echo    PID: %%a
    )
    echo    http://localhost:8000
)

echo.
echo Frontend (port 8501):
netstat -ano | findstr :8501 | findstr LISTENING >nul
if errorlevel 1 (
    echo    [STOPPED]
) else (
    echo    [RUNNING]
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501 ^| findstr LISTENING') do (
        echo    PID: %%a
    )
    echo    http://localhost:8501
)

echo.
pause
goto menu

:install
cls
echo ========================================
echo    Installing Dependencies
echo ========================================
echo.

cd /d "%~dp0app"

echo Installing/Updating...
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo Install failed!
) else (
    echo Install complete!
)

pause
goto menu

:clean
cls
echo ========================================
echo    Cleaning Cache
echo ========================================
echo.

cd /d "%~dp0app"

echo Cleaning Python cache...
del /s /q *.pyc >nul 2>&1
rmdir /s /q __pycache__ >nul 2>&1

echo Cleaning Streamlit cache...
rmdir /s /q "%USERPROFILE%\.streamlit\cache" >nul 2>&1

echo Clean complete!
pause
goto menu