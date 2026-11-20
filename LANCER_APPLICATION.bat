@echo off
title Bibliotheque Pro - Dashboard
cd /d "%~dp0"
echo ========================================================
echo   DEMARRAGE DE L'APPLICATION GESTION BIBLIOTHEQUE
echo ========================================================
start "" "http://127.0.0.1:5000"
python app_web.py
pause

