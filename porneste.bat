@echo off
chcp 65001 >nul
title Lansator CodeSpace
cd /d "%~dp0"

echo.
echo   ============================================
echo       CodeSpace - se porneste aplicatia
echo   ============================================
echo.
echo   [1/3] Pornesc backend-ul (serverul)...
start "CodeSpace - Backend"  /D "%~dp0"          cmd /k python run.py

echo   [2/3] Pornesc frontend-ul (interfata)...
start "CodeSpace - Frontend" /D "%~dp0frontend"  cmd /k npm run dev

echo   [3/3] Astept pornirea (cca. 12 secunde) si deschid browserul...
timeout /t 12 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo   Gata! Aplicatia s-a deschis in browser:  http://localhost:5173
echo   (Daca pagina nu se incarca din prima, asteapta 5 secunde si reincarca.)
echo.
echo   IMPORTANT: lasa cele doua ferestre noi (Backend si Frontend)
echo   DESCHISE cat timp folosesti aplicatia. Cand termini, le inchizi.
echo.
echo   Aceasta fereastra se poate inchide.
echo.
pause
