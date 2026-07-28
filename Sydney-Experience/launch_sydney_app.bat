@echo off
chcp 65001 >nul
title Sydney 月窗
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch_app.ps1"
if errorlevel 1 pause
