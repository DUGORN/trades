@echo off
color 0A
title Trading Tools - Binance Futures

:menu
cls
echo ========================================
echo    TRADING TOOLS - BINANCE FUTURES
echo ========================================
echo.
echo 1. Custom Ranking (Choose Sort)
echo 2. Quick Scan (By Score)
echo 3. Check Watchlist
echo 4. Check Single Coin
echo 5. Add New Coin
echo 6. Remove Coin
echo 7. Scan and Ask AI
echo 8. Open OpenCode
echo 9. Start Web App (Mobile)
echo 10. Trade Logger
echo 11. Remove Duplicates
echo 12. Exit
echo.
echo ========================================
set /p choice="Select (1-12): "

if "%choice%"=="1" goto customrank
if "%choice%"=="2" goto quickscan
if "%choice%"=="3" goto watchlist
if "%choice%"=="4" goto single
if "%choice%"=="5" goto addcoin
if "%choice%"=="6" goto removecoin
if "%choice%"=="7" goto scanask
if "%choice%"=="8" goto opencode
if "%choice%"=="9" goto webapp
if "%choice%"=="10" goto tradelog
if "%choice%"=="11" goto dedup
if "%choice%"=="12" goto end

echo.
echo ❌ Invalid choice! Press Enter to continue...
pause >nul
goto menu

:customrank
cls
python custom_rank.py
echo.
pause
goto menu

:quickscan
cls
echo.
echo Quick Scan by Score...
echo.
python rank_setups.py
echo.
pause
goto menu

:watchlist
cls
echo.
echo Checking watchlist...
echo.
python check_watchlist.py
echo.
pause
goto menu

:single
cls
echo.
set /p coin="Enter coin (e.g., BTCUSDT): "
python quick_check.py %coin%
echo.
pause
goto menu

:addcoin
cls
echo.
python add_coin.py
echo.
pause
goto menu

:removecoin
cls
echo.
python remove_coin.py
echo.
pause
goto menu

:scanask
cls
python scan_and_ask.py
echo.
pause
goto menu

:opencode
cls
echo.
echo Opening OpenCode...
echo.
start opencode
goto menu

:webapp
cls
echo.
echo Starting Web App for Mobile...
echo.
echo On mobile, open: http://[YOUR-IP]:5000
echo.
start cmd /k "python app.py"
goto menu

:tradelog
cls
python trade_logger.py
echo.
pause
goto menu

:dedup
cls
python remove_duplicates.py
echo.
pause
goto menu

:end
exit