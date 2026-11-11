@echo off
chcp 65001 >nul
rem Thin wrapper so there is a single implementation (demo_web.ps1).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0demo_web.ps1" %*
