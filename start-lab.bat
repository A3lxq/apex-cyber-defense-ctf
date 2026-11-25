@echo off
title Apex Cyber Defense - Exam Lab Launcher
cls
echo =====================================================================
echo    Apex Cyber Defense - Network Pentesting Exam Lab
echo =====================================================================
echo.
echo  Folder Location: %~dp0
echo.
echo  Choose an option:
echo   [1] Open Lab folder in Windows File Explorer
echo   [2] View Student Exam Brief
echo   [3] View Solution Walkthrough
echo   [4] View Instructor Manual
echo   [5] Check Docker availability
echo   [6] Exit
echo.
set /p opt="Enter option (1-6): "

if "%opt%"=="1" (
    explorer "%~dp0"
    goto end
)
if "%opt%"=="2" (
    notepad "%~dp0docs\EXAM_BRIEF_FOR_STUDENTS.md"
    goto end
)
if "%opt%"=="3" (
    notepad "%~dp0docs\SOLUTION_WALKTHROUGH.md"
    goto end
)
if "%opt%"=="4" (
    notepad "%~dp0docs\INSTRUCTOR_MANUAL.md"
    goto end
)
if "%opt%"=="5" (
    echo.
    echo Checking for Docker...
    docker --version 2>nul
    if %errorlevel% neq 0 (
        echo [!] Docker is not installed or not in PATH on this Windows host.
        echo [*] To run the live target container, install Docker Desktop or deploy
        echo     this folder to an Ubuntu/Debian VM using setup-exam.sh.
    ) else (
        echo [OK] Docker found! You can launch the lab using:
        echo      docker compose up -d --build
    )
    pause
    goto end
)

:end
