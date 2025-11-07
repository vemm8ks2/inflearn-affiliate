@echo off
REM 인프런 강의 스크래핑 실행 스크립트 (Windows)

echo ================================================
echo 인프런 강의 스크래핑 시작
echo ================================================
echo.

REM 스크립트 디렉토리로 이동
cd /d "%~dp0scripts"

REM Python 스크립트 실행
echo [실행] 스크래핑 중...
..\venv\Scripts\python.exe -m src.scraper

echo.
echo ================================================
echo 실행 완료
echo ================================================
echo.

pause
