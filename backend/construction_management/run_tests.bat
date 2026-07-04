@echo off
REM Test Runner for Construction Management App
REM This script runs all automated tests

echo.
echo ============================================================
echo  CONSTRUCTION MANAGEMENT APP - TEST RUNNER
echo ============================================================
echo.

REM Check if pytest is installed
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pytest is not installed
    echo Install with: pip install -r requirements-test.txt
    pause
    exit /b 1
)

REM Set environment
set FLASK_ENV=testing
set TESTING=True

echo [INFO] Running Tests...
echo [INFO] Environment: TESTING
echo [INFO] Database: tests.db
echo.

REM Create tests directory if it doesn't exist
if not exist tests mkdir tests

REM Run pytest with options
echo [TEST] Running Backend API Tests...
python -m pytest tests/ -v --html=test_report.html --self-contained-html -x
if errorlevel 1 (
    echo.
    echo [FAILED] Some tests failed. See test_report.html for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  ALL TESTS PASSED!
echo ============================================================
echo.
echo Report: test_report.html
echo Database: tests.db
echo.
pause
