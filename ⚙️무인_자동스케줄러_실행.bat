@echo off
chcp 65001 > nul
title Q-TAP Automated Scheduler Daemon
cd /d "%~dp0"

echo ==========================================================
echo   ⚙️ Q-TAP 무인 자동 스케줄러 데몬 실행 중...
echo ==========================================================
echo.
echo  - 매일 오전 06:30 (미국장 마감 분석)
echo  - 매일 오전 08:30 (한국장 개장 전 분석)
echo  - 분석 완료 시 스마트폰 텔레그램으로 자동 보고서 발송
echo.
echo  이 창을 켜두시면 백그라운드에서 매일 자동으로 분석합니다.
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [오류] 가상환경이 발견되지 않았습니다.
    pause
    exit /b
)

.venv\Scripts\python.exe src\scheduler.py

pause
