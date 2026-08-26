@echo off
title Uttarakhand Disaster Relief Portal
color 0A
echo ===================================================
echo   UTTARAKHAND DISASTER MANAGEMENT SYSTEM (STARTUP)
echo ===================================================
echo.
echo [1/2] Checking and initializing database...
python sample_data.py
echo.
echo [2/2] Launching Web Portal in your browser...
echo.
python -m streamlit run app.py
pause
