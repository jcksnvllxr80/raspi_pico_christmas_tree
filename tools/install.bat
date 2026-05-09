@echo off
setlocal EnableDelayedExpansion

:: ─────────────────────────────────────────────────────────────────────────────
::  Pico Christmas Tree Installer  (Windows)
::
::  Usage:
::    install.bat              -- remove_wifi_and_clock branch (no wifi/clock)
::    install.bat -w|--wifi    -- master branch (full wifi + clock)
::    install.bat -p|--pineapple -- led-pineapple branch
::
::  Installs git, Python 3.11, and mpremote if not already present.
::  Uses winget when available; falls back to direct download via PowerShell
::  for machines where winget is missing (older Win10, LTSC, etc.).
::  Everything installed by this script is removed automatically afterward.
:: ─────────────────────────────────────────────────────────────────────────────

set "BRANCH=remove_wifi_and_clock"
set "DO_WIFI=0"

:arg_loop
if "%~1"=="" goto args_done
if /I "%~1"=="-w"          ( set "BRANCH=master"        & set "DO_WIFI=1" & shift & goto arg_loop )
if /I "%~1"=="--wifi"      ( set "BRANCH=master"        & set "DO_WIFI=1" & shift & goto arg_loop )
if /I "%~1"=="-p"          ( set "BRANCH=led-pineapple" & shift & goto arg_loop )
if /I "%~1"=="--pineapple" ( set "BRANCH=led-pineapple" & shift & goto arg_loop )
if /I "%~1"=="-h"          goto show_usage
if /I "%~1"=="--help"      goto show_usage
echo  Unknown option: %~1
goto show_usage
:args_done

echo.
echo  ============================================
echo   Pico Christmas Tree Installer  [Windows]
echo   Branch : %BRANCH%
echo  ============================================
echo.

:: Track what this script installs so we only remove what we added
set "INSTALLED_GIT=0"
set "INSTALLED_PYTHON=0"
set "INSTALLED_MPREMOTE=0"
set "CLONEDIR="

:: ── Detect existing Python ────────────────────────────────────────────────────
set "PY="
python --version >nul 2>&1 && set "PY=python"
if not defined PY (
    py --version >nul 2>&1 && set "PY=py"
)

:: ─────────────────────────────────────────────────────────────────────────────
:: 1. Git
:: ─────────────────────────────────────────────────────────────────────────────
echo [1/4] Checking Git...
git --version >nul 2>&1
if %ERRORLEVEL% equ 0 goto git_ok

echo       Not found. Will install.
set "INSTALLED_GIT=1"

:: Try winget first
winget --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo       winget found - installing Git...
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent
    if %ERRORLEVEL% equ 0 goto git_path_setup
    echo       winget install failed - falling back to direct download...
) else (
    echo       winget not available - downloading Git directly...
)

:: PowerShell fallback: fetch latest Git for Windows from GitHub releases API
set "GIT_EXE=%TEMP%\git-setup-%RANDOM%.exe"
set "GIT_PS=%TEMP%\pico_git_%RANDOM%.ps1"

echo $r = Invoke-RestMethod 'https://api.github.com/repos/git-for-windows/git/releases/latest' > "!GIT_PS!"
echo $asset = $r.assets ^| Where-Object { $_.name -match 'Git-[\d.]+-64-bit\.exe$' } ^| Select-Object -First 1 >> "!GIT_PS!"
echo if (-not $asset) { Write-Error 'Could not find Git installer asset'; exit 1 } >> "!GIT_PS!"
echo Write-Host ('Downloading ' + $asset.browser_download_url) >> "!GIT_PS!"
echo Invoke-WebRequest -Uri $asset.browser_download_url -OutFile '!GIT_EXE!' -UseBasicParsing >> "!GIT_PS!"

powershell -NoProfile -ExecutionPolicy Bypass -File "!GIT_PS!"
del "!GIT_PS!" 2>nul

if not exist "!GIT_EXE!" (
    echo.
    echo  ERROR: Could not download the Git installer.
    echo  Please install Git manually from https://git-scm.com and re-run.
    goto do_cleanup
)

echo       Running Git installer silently...
"!GIT_EXE!" /VERYSILENT /NORESTART /NOCANCEL /SP-
del "!GIT_EXE!" 2>nul

:git_path_setup
set "PATH=%PATH%;C:\Program Files\Git\cmd"
git --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  Git was installed but is not yet on PATH.
    echo  Close this window, open a new terminal, and re-run install.bat.
    goto do_cleanup
)

:git_ok
for /f "tokens=*" %%v in ('git --version 2^>nul') do echo       OK  ^(%%v^)
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: 2. Python
:: ─────────────────────────────────────────────────────────────────────────────
echo [2/4] Checking Python...
if defined PY goto python_ok

echo       Not found. Will install.
set "INSTALLED_PYTHON=1"

:: Try winget first
winget --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo       winget found - installing Python 3.11...
    winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements --silent
    if %ERRORLEVEL% equ 0 goto python_path_setup
    echo       winget install failed - falling back to direct download...
) else (
    echo       winget not available - downloading Python directly...
)

:: PowerShell fallback: download Python 3.11 installer from python.org
:: Pin to 3.11.9 (latest 3.11.x stable). Update this URL if a newer patch is released.
set "PY_EXE=%TEMP%\python-setup-%RANDOM%.exe"
set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

echo       Downloading %PY_URL%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '!PY_EXE!' -UseBasicParsing"
if not exist "!PY_EXE!" (
    echo.
    echo  ERROR: Could not download the Python installer.
    echo  Please install Python from https://python.org and re-run.
    goto do_cleanup
)

echo       Running Python installer silently (per-user, no elevation required^)...
"!PY_EXE!" /quiet InstallAllUsers=0 PrependPath=1 Include_tcltk=1
del "!PY_EXE!" 2>nul

:python_path_setup
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
python --version >nul 2>&1 && set "PY=python"
if not defined PY (
    echo  Python was installed but is not yet on PATH.
    echo  Close this window, open a new terminal, and re-run install.bat.
    goto do_cleanup
)

:python_ok
for /f "tokens=*" %%v in ('!PY! --version 2^>nul') do echo       OK  ^(%%v^)
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: 3. mpremote
:: ─────────────────────────────────────────────────────────────────────────────
echo [3/4] Checking mpremote...
!PY! -m mpremote version >nul 2>&1
if %ERRORLEVEL% equ 0 goto mpremote_ok

echo       Not found. Installing via pip...
!PY! -m pip install --upgrade mpremote
if %ERRORLEVEL% neq 0 (
    echo  ERROR: pip install mpremote failed.
    goto do_cleanup
)
!PY! -m mpremote version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  ERROR: mpremote installed but not importable. Check pip output above.
    goto do_cleanup
)
set "INSTALLED_MPREMOTE=1"

:mpremote_ok
for /f "tokens=*" %%v in ('!PY! -m mpremote version 2^>nul') do echo       OK  ^(%%v^)
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: 4. Clone repo
:: ─────────────────────────────────────────────────────────────────────────────
echo [4/4] Cloning repository  (branch: %BRANCH%)...
set "REPO_URL=https://github.com/jcksnvllxr80/raspi_pico_christmas_tree.git"
set "CLONEDIR=%TEMP%\pico_xmas_%RANDOM%"
git clone --branch %BRANCH% --depth 1 "%REPO_URL%" "%CLONEDIR%"
if %ERRORLEVEL% neq 0 (
    echo  ERROR: git clone failed.
    goto do_cleanup
)
echo       OK  ^(%CLONEDIR%^)
echo.

cd /d "%CLONEDIR%"

:: ─────────────────────────────────────────────────────────────────────────────
:: WiFi config  (master branch only)
:: ─────────────────────────────────────────────────────────────────────────────
if %DO_WIFI%==1 (
    echo Collecting WiFi credentials...

    set "DIALOG_PY=%TEMP%\pico_dialog_%RANDOM%.py"
    set "SSID_FILE=%TEMP%\pico_ssid_%RANDOM%.txt"
    set "PW_FILE=%TEMP%\pico_pw_%RANDOM%.txt"

    echo import sys > "!DIALOG_PY!"
    echo import tkinter as tk >> "!DIALOG_PY!"
    echo from tkinter import simpledialog, messagebox >> "!DIALOG_PY!"
    echo root = tk.Tk() >> "!DIALOG_PY!"
    echo root.withdraw() >> "!DIALOG_PY!"
    echo root.call('wm', 'attributes', '.', '-topmost', True) >> "!DIALOG_PY!"
    echo ssid = simpledialog.askstring('Pico Tree  -  WiFi Setup', 'Enter WiFi SSID:', parent=root) or '' >> "!DIALOG_PY!"
    echo if not ssid: >> "!DIALOG_PY!"
    echo     messagebox.showerror('Pico Tree', 'SSID cannot be empty.') >> "!DIALOG_PY!"
    echo     sys.exit(1) >> "!DIALOG_PY!"
    echo pw = simpledialog.askstring('Pico Tree  -  WiFi Setup', 'Enter WiFi Password:', show='*', parent=root) or '' >> "!DIALOG_PY!"
    echo open(sys.argv[1], 'w', encoding='utf-8').write(ssid) >> "!DIALOG_PY!"
    echo open(sys.argv[2], 'w', encoding='utf-8').write(pw) >> "!DIALOG_PY!"

    !PY! "!DIALOG_PY!" "!SSID_FILE!" "!PW_FILE!"
    if %ERRORLEVEL% neq 0 (
        echo  ERROR: Credential dialog failed or was cancelled.
        del "!DIALOG_PY!" 2>nul
        goto do_cleanup
    )
    del "!DIALOG_PY!" 2>nul

    if not exist "!SSID_FILE!" (
        echo  ERROR: SSID file was not created.
        goto do_cleanup
    )

    set /p "SSID=" < "!SSID_FILE!"
    set /p "WIFIPASS=" < "!PW_FILE!"
    del "!SSID_FILE!" 2>nul
    del "!PW_FILE!"  2>nul

    if "!SSID!"=="" (
        echo  ERROR: SSID cannot be empty.
        goto do_cleanup
    )

    echo Generating config.json from credentials...
    :: Use env vars to safely pass creds to Python (avoids quoting issues)
    set "SSID=!SSID!"
    set "WIFIPASS=!WIFIPASS!"
    !PY! -c "import json,base64,os;c=json.load(open('conf/example_config.json'));c['wifi']['ssid']=base64.b64encode(os.environ['SSID'].encode()).decode();c['wifi']['password']=base64.b64encode(os.environ['WIFIPASS'].encode()).decode();json.dump(c,open('conf/config.json','w'),indent=2)"
    if %ERRORLEVEL% neq 0 (
        echo  ERROR: Failed to generate config.json.
        goto do_cleanup
    )
    echo Done.
    echo.
)

:: ─────────────────────────────────────────────────────────────────────────────
:: Upload files via mpremote
:: ─────────────────────────────────────────────────────────────────────────────
set "MP=!PY! -m mpremote"

echo Uploading files to Pico...

if %DO_WIFI%==1 (
    echo   Creating /conf directory on Pico (safe to ignore if already exists^)...
    !MP! fs mkdir /conf 2>nul

    echo   Uploading master branch files...
    !MP! cp main.py                  :main.py                  || goto upload_err
    !MP! cp img\img_utils.py         :img_utils.py             || goto upload_err
    !MP! cp base64\base64.py         :base64.py                || goto upload_err
    !MP! cp display\ssd1306.py       :ssd1306.py               || goto upload_err
    !MP! cp eeprom\EEPROM_24LC512.py :EEPROM_24LC512.py        || goto upload_err
    !MP! cp http\httpParser.py       :httpParser.py            || goto upload_err
    !MP! cp neopixel\neopixel.py     :neopixel.py              || goto upload_err
    !MP! cp wifi\esp8266.py          :esp8266.py               || goto upload_err
    !MP! cp conf\config.json         :conf/config.json         || goto upload_err

    del conf\config.json 2>nul
) else (
    echo   Uploading files...
    !MP! cp main.py                  :main.py                  || goto upload_err
    !MP! cp img\img_utils.py         :img_utils.py             || goto upload_err
    !MP! cp display\ssd1306.py       :ssd1306.py               || goto upload_err
    !MP! cp eeprom\EEPROM_24LC512.py :EEPROM_24LC512.py        || goto upload_err
    !MP! cp neopixel\neopixel.py     :neopixel.py              || goto upload_err
)

goto do_cleanup

:upload_err
echo.
echo  ERROR: A file failed to upload. Check that the Pico is connected via a data-capable USB cable.

:: ─────────────────────────────────────────────────────────────────────────────
:: Cleanup  (all paths — success and error — end here)
:: ─────────────────────────────────────────────────────────────────────────────
:do_cleanup
echo.
echo Cleaning up...

cd /d "%TEMP%"

if defined CLONEDIR (
    if exist "%CLONEDIR%" (
        rd /s /q "%CLONEDIR%"
        echo   Repo clone removed.
    )
)

if %INSTALLED_MPREMOTE%==1 (
    echo   Uninstalling mpremote...
    !PY! -m pip uninstall -y mpremote pyserial >nul 2>&1
    echo   mpremote uninstalled.
)

if %INSTALLED_PYTHON%==1 (
    echo   Uninstalling Python 3.11...
    winget uninstall --id Python.Python.3.11 --silent >nul 2>&1
    echo   Python uninstalled.
)

if %INSTALLED_GIT%==1 (
    echo   Uninstalling Git...
    winget uninstall --id Git.Git --silent >nul 2>&1
    echo   Git uninstalled.
)

echo.
echo  ============================================
echo   Done!  Pico updated successfully.
echo   Branch : %BRANCH%
echo  ============================================
echo.
exit /b 0

:: ─────────────────────────────────────────────────────────────────────────────
:: Usage  (shown for -h / --help / unknown flags)
:: ─────────────────────────────────────────────────────────────────────────────
:show_usage
echo.
echo  Usage: install.bat [OPTION]
echo.
echo  Options:
echo    (none)              Flash remove_wifi_and_clock branch  (LEDs, no wifi/clock)
echo    -w, --wifi          Flash master branch  (LEDs + OLED + wifi + NTP clock)
echo    -p, --pineapple     Flash led-pineapple branch
echo    -h, --help          Show this help
echo.
echo  Requirements:
echo    - Pico connected via a data-capable USB cable
echo    - Internet connection  (for cloning the repo and downloading dependencies)
echo.
echo  Dependencies (git, Python 3.11, mpremote) are installed automatically
echo  if missing and are removed again when the script finishes.
echo.
