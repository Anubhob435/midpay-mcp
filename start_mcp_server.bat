@echo off
REM MidPay MCP Server Startup Script for Windows

echo Starting MidPay MCP Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import midpay, pymongo, dotenv, cryptography" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Set environment variables if .env file exists
if exist .env (
    echo Loading environment variables from .env file
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        set "%%a=%%b"
    )
)

echo.
echo MidPay MCP Server is starting...
echo Connect this server to your AI client using the Model Context Protocol
echo Use Ctrl+C to stop the server
echo.

REM Run the MCP server
python simple_mcp_server.py

pause
