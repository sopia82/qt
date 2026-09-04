@echo off
chcp 65001 > nul
title Q-TAP Quantum Trading Terminal
cd /d "%~dp0"

echo ==========================================================
echo   🚀 Q-TAP 퀀텀 트레이딩 로컬호스트 웹 터미널 실행 중...
echo ==========================================================
echo.
echo  잠시 후 웹 브라우저가 자동으로 실행됩니다 (http://127.0.0.1:5000)
echo  종료하려면 이 창을 닫거나 Ctrl + C를 누르세요.
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [오류] 가상환경이 발견되지 않았습니다.
    pause
    exit /b
)

.venv\Scripts\python.exe app.py

pause
