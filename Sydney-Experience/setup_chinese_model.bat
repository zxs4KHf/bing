@echo off
chcp 65001 >nul
title Sydney 月窗 - 中文增强模型
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup_chinese_model.ps1"
if errorlevel 1 pause
