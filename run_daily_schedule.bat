@echo off

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PROJECT_DIR=D:\04code\code\ST-dailyreport
set RUNTIME_LOG_DIR=%PROJECT_DIR%\runtime\logs
set LOG_FILE=%RUNTIME_LOG_DIR%\daily_schedule.log

if not exist "%RUNTIME_LOG_DIR%" mkdir "%RUNTIME_LOG_DIR%"

echo ============================================================ >> "%LOG_FILE%" 2>&1
echo [%date% %time%] ST-Dailyreport daily task started >> "%LOG_FILE%" 2>&1
echo ============================================================ >> "%LOG_FILE%" 2>&1

cd /d "%PROJECT_DIR%"

REM --- Preflight: validate scheduled task contract before doing work ---
if not "%SKIP_GOVERNANCE_HEALTH_CHECK%"=="1" (
    if exist "%PROJECT_DIR%\tools\health_check.py" (
        echo [%date% %time%] Preflight: running governance health check ... >> "%LOG_FILE%" 2>&1
        python tools\health_check.py >> "%LOG_FILE%" 2>&1
        if errorlevel 1 (
            echo [%date% %time%] ERROR: Governance health check failed >> "%LOG_FILE%" 2>&1
            exit /b 1
        )
        echo [%date% %time%] Preflight: governance health check passed >> "%LOG_FILE%" 2>&1
    ) else (
        echo [%date% %time%] WARNING: Governance health check script not found; continuing >> "%LOG_FILE%" 2>&1
    )
)

REM --- Step 1: Generate daily report ---
echo [%date% %time%] Step 1/3: Generating daily report ... >> "%LOG_FILE%" 2>&1
python run_daily_report.py >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [%date% %time%] ERROR: Report generation failed >> "%LOG_FILE%" 2>&1
    exit /b 1
)
echo [%date% %time%] Step 1/3: Report generation done >> "%LOG_FILE%" 2>&1

REM --- Step 2: Git push to Gitee ---
echo [%date% %time%] Step 2/3: Pushing to Gitee ... >> "%LOG_FILE%" 2>&1
python git_push.py >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [%date% %time%] WARNING: Git push failed >> "%LOG_FILE%" 2>&1
) else (
    echo [%date% %time%] Step 2/3: Git push done >> "%LOG_FILE%" 2>&1
)

REM --- Step 3: WeChat sync ---
echo [%date% %time%] Step 3/3: Syncing to WeChat ... >> "%LOG_FILE%" 2>&1
python daily_task_win.py >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [%date% %time%] WARNING: WeChat sync failed >> "%LOG_FILE%" 2>&1
) else (
    echo [%date% %time%] Step 3/3: WeChat sync done >> "%LOG_FILE%" 2>&1
)

echo [%date% %time%] All tasks completed >> "%LOG_FILE%" 2>&1
echo ============================================================ >> "%LOG_FILE%" 2>&1

exit /b 0
