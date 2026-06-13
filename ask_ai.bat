@echo off
cls
echo ========================================
echo    QUICK ASK OPENCODE
echo ========================================
echo.

set /p symbol="Symbol (e.g., XLMUSDT.P): "
set /p price="Current Price: "
set /p pdl="PDL: "
set /p pdh="PDH: "
set /p sweep="Sweep Price: "
set /p v6="V6 (BUY/SELL): "
set /p waterfall="Waterfall (COLD/HOT): "
set /p cdv="CDV (RISING/FALLING): "
set /p htf="HTF Bias (BULLISH/BEARISH/NEUTRAL): "
set /p gaussian="Gaussian (BULL/BEAR): "

echo.
echo Opening OpenCode with your data...
echo.

start opencode
timeout /t 3 >nul

echo Copy this to OpenCode:
echo.
echo %symbol% - MANDATORY PRICE LEVELS
echo.
echo Current Price: %price%
echo Leverage: 75x
echo Portfolio: $1000
echo Risk per trade: 1%% ($10)
echo.
echo DATA:
echo - Sweep Low: %sweep%
echo - PDL: %pdl%
echo - PDH: %pdh%
echo - V6: %v6%
echo - CDV: %cdv%
echo - Waterfall: %waterfall%
echo - Gaussian: %gaussian%
echo - HTF: %htf%
echo.
echo REQUIRED:
echo Entry (within 0.3%%)
echo SL (max 1%%)
echo TP1 (1-2%%)
echo TP2 (2-3%%)
echo.
echo Format:
echo Entry: _____
echo SL: _____
echo TP1: _____
echo TP2: _____
echo R:R = _____
echo Size: $_____

pause