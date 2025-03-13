@echo off
setlocal enabledelayedexpansion

echo Pokemon SV Trainer Data Scraper
echo ==============================
echo.

:menu
echo Choose an option:
echo 1. Install dependencies
echo 2. Test Google Sheets API connection
echo 3. Run scraper (default settings)
echo 4. Run scraper with custom settings
echo 5. Upload existing data to Google Sheets
echo 6. Run GUI application
echo 7. Exit
echo.

set /p choice=Enter your choice (1-7): 

if "%choice%"=="1" (
    call :install_deps
    goto menu
) else if "%choice%"=="2" (
    call :test_connection
    goto menu
) else if "%choice%"=="3" (
    call :run_default
    goto menu
) else if "%choice%"=="4" (
    call :run_custom
    goto menu
) else if "%choice%"=="5" (
    call :upload_data
    goto menu
) else if "%choice%"=="6" (
    call :run_gui
    goto menu
) else if "%choice%"=="7" (
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    echo.
    goto menu
)

:install_deps
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Dependencies installed.
echo.
pause
exit /b 0

:test_connection
echo.
echo Testing connection to Google Sheets API...
python test_connection.py
echo.
pause
exit /b 0

:run_default
echo.
echo Running scraper with default settings...
python main.py --limit 10
echo.
pause
exit /b 0

:run_custom
echo.
set /p limit=Enter limit (number of trainers to scrape, 0 for all): 
set /p delay=Enter delay between requests in seconds (default: 1.0): 
set /p output=Enter output file name (default: trainer_data.json): 
set /p upload=Upload to Google Sheets? (y/n): 

set cmd=python main.py

if not "%limit%"=="" (
    set cmd=!cmd! --limit %limit%
)

if not "%delay%"=="" (
    set cmd=!cmd! --delay %delay%
)

if not "%output%"=="" (
    set cmd=!cmd! --output %output%
)

if /i "%upload%"=="y" (
    set cmd=!cmd! --upload
    
    set /p spreadsheet=Enter spreadsheet name (default: Pokemon SV Trainer Data): 
    set /p credentials=Enter credentials file path (default: credentials.json): 
    
    if not "%spreadsheet%"=="" (
        set cmd=!cmd! --spreadsheet "%spreadsheet%"
    )
    
    if not "%credentials%"=="" (
        set cmd=!cmd! --credentials "%credentials%"
    )
)

echo.
echo Running command: !cmd!
echo.
!cmd!
echo.
pause
exit /b 0

:upload_data
echo.
set /p json_file=Enter JSON file to upload (default: trainer_data.json): 
set /p spreadsheet=Enter spreadsheet name (default: Pokemon SV Trainer Data): 
set /p credentials=Enter credentials file path (default: credentials.json): 

if "%json_file%"=="" set json_file=trainer_data.json
if "%spreadsheet%"=="" set spreadsheet=Pokemon SV Trainer Data
if "%credentials%"=="" set credentials=credentials.json

echo.
echo Uploading %json_file% to Google Sheets...
python -c "from sheets_uploader import upload_to_sheets; upload_to_sheets('%json_file%', '%spreadsheet%', '%credentials%')"
echo.
pause
exit /b 0

:run_gui
echo.
echo Running GUI application...
python gui_app.py
echo.
pause
exit /b 0 