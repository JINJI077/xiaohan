@echo off
setlocal

cd /d "%~dp0"

if "%PORT%"=="" (
  set "APP_PORT=5173"
) else (
  set "APP_PORT=%PORT%"
)

echo.
echo ADHD Launcher - local AI proxy
echo =================================
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo Node.js was not found.
  echo Please install Node.js 18 or newer, then run start.bat again.
  echo Download: https://nodejs.org/
  echo.
  pause
  exit /b 1
)

for /f %%V in ('node -p "process.versions.node.split('.')[0]" 2^>nul') do set "NODE_MAJOR=%%V"
if not defined NODE_MAJOR (
  echo Could not read the Node.js version.
  echo Please reinstall Node.js 18 or newer, then run start.bat again.
  echo.
  pause
  exit /b 1
)

if %NODE_MAJOR% LSS 18 (
  echo Your Node.js major version is %NODE_MAJOR%.
  echo This project requires Node.js 18 or newer.
  echo Please upgrade Node.js, then run start.bat again.
  echo.
  pause
  exit /b 1
)

echo Node.js check passed.
echo Opening: http://127.0.0.1:%APP_PORT%/
echo Keep this window open while using AI.
echo.

start "" "http://127.0.0.1:%APP_PORT%/"
node local-proxy.mjs

echo.
echo Local proxy stopped.
echo If the port is busy, run this in Command Prompt:
echo set PORT=3000 ^&^& start.bat
echo.
pause
