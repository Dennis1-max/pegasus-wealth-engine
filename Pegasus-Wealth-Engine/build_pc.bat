@echo off
REM Pegasus Wealth Engine - Windows PC EXE Build Script
REM Builds the PWE Kivy app into a Windows executable using PyInstaller

echo 🚀 Starting Windows EXE build for Pegasus Wealth Engine...

REM Check if we're in the right directory
if not exist "pwe_app" (
    echo ❌ Error: pwe_app directory not found. Please run this script from the Pegasus-Wealth-Engine root directory.
    pause
    exit /b 1
)

echo 🖥️ Building Windows EXE for PWE App...

REM Navigate to the app directory
cd pwe_app

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ from python.org
    echo 📋 Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found! Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo ✅ pip found

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install PyInstaller if not available
echo 📦 Installing/upgrading PyInstaller...
pip install --upgrade pyinstaller

REM Install PWE requirements
echo 📦 Installing PWE dependencies...
pip install -r requirements.txt

REM Install additional dependencies for Windows build
echo 📦 Installing Windows-specific dependencies...
pip install pywin32 pywin32-ctypes

REM Create the spec file for PyInstaller
echo ⚙️ Creating PyInstaller spec file...

echo # -*- mode: python ; coding: utf-8 -*- > pwe.spec
echo. >> pwe.spec
echo block_cipher = None >> pwe.spec
echo. >> pwe.spec
echo a = Analysis^( >> pwe.spec
echo     ['main.py'], >> pwe.spec
echo     pathex=[], >> pwe.spec
echo     binaries=[], >> pwe.spec
echo     datas=[ >> pwe.spec
echo         ('config.py', '.'), >> pwe.spec
echo         ('../pwe_bots', 'pwe_bots'), >> pwe.spec
echo     ], >> pwe.spec
echo     hiddenimports=[ >> pwe.spec
echo         'kivy.deps.angle', >> pwe.spec
echo         'kivy.deps.glew', >> pwe.spec
echo         'kivy.deps.sdl2', >> pwe.spec
echo         'win32timezone', >> pwe.spec
echo         'pwe_bots.blog_bot', >> pwe.spec
echo         'pwe_bots.ebook_bot', >> pwe.spec
echo         'pwe_bots.freelance_bot', >> pwe.spec
echo         'pwe_bots.email_bot', >> pwe.spec
echo         'sqlite3', >> pwe.spec
echo         'requests', >> pwe.spec
echo         'schedule', >> pwe.spec
echo         'speech_recognition', >> pwe.spec
echo     ], >> pwe.spec
echo     hookspath=[], >> pwe.spec
echo     hooksconfig={}, >> pwe.spec
echo     runtime_hooks=[], >> pwe.spec
echo     excludes=[], >> pwe.spec
echo     win_no_prefer_redirects=False, >> pwe.spec
echo     win_private_assemblies=False, >> pwe.spec
echo     cipher=block_cipher, >> pwe.spec
echo     noarchive=False, >> pwe.spec
echo ^) >> pwe.spec
echo. >> pwe.spec
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^) >> pwe.spec
echo. >> pwe.spec
echo exe = EXE^( >> pwe.spec
echo     pyz, >> pwe.spec
echo     a.scripts, >> pwe.spec
echo     a.binaries, >> pwe.spec
echo     a.zipfiles, >> pwe.spec
echo     a.datas, >> pwe.spec
echo     [], >> pwe.spec
echo     name='Pegasus_Wealth_Engine', >> pwe.spec
echo     debug=False, >> pwe.spec
echo     bootloader_ignore_signals=False, >> pwe.spec
echo     strip=False, >> pwe.spec
echo     upx=True, >> pwe.spec
echo     upx_exclude=[], >> pwe.spec
echo     runtime_tmpdir=None, >> pwe.spec
echo     console=False, >> pwe.spec
echo     disable_windowed_traceback=False, >> pwe.spec
echo     argv_emulation=False, >> pwe.spec
echo     target_arch=None, >> pwe.spec
echo     codesign_identity=None, >> pwe.spec
echo     entitlements_file=None, >> pwe.spec
echo     icon='app_icon.ico', >> pwe.spec
echo ^) >> pwe.spec

echo ✅ PyInstaller spec file created

REM Create a simple app icon (optional)
if not exist "app_icon.ico" (
    echo 🎨 Creating default app icon...
    REM This would normally create an icon file, but for simplicity we'll skip it
    echo # No icon file created - using default
)

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo 🧹 Cleaned previous builds

REM Build the EXE
echo 🔨 Building Windows EXE... (This may take 5-15 minutes)
echo ⏳ Please be patient, compiling dependencies...

REM Build using the spec file
pyinstaller --noconfirm pwe.spec

REM Check if build was successful
if exist "dist\Pegasus_Wealth_Engine.exe" (
    echo ✅ EXE build completed successfully!
    
    REM Get file size
    for %%A in ("dist\Pegasus_Wealth_Engine.exe") do set EXE_SIZE=%%~zA
    set /a EXE_SIZE_MB=%EXE_SIZE% / 1024 / 1024
    echo 📊 EXE size: %EXE_SIZE_MB% MB
    
    REM Copy EXE to project root for easy access
    copy "dist\Pegasus_Wealth_Engine.exe" "..\Pegasus_Wealth_Engine.exe"
    echo 📋 EXE copied to: ..\Pegasus_Wealth_Engine.exe
    
    echo.
    echo 🎉 SUCCESS! Your Pegasus Wealth Engine EXE is ready!
    echo.
    echo 🖥️ Installation Instructions:
    echo 1. The EXE file is ready to run: Pegasus_Wealth_Engine.exe
    echo 2. No installation required - just double-click to run
    echo 3. Windows may show a security warning - click "More info" then "Run anyway"
    echo 4. The app will create local database files in the same directory
    echo.
    echo ⚠️ Note: First run may take longer as Windows loads dependencies
    echo.
    
    REM Create a launcher script
    echo @echo off > "..\Run_PWE.bat"
    echo echo 🚀 Starting Pegasus Wealth Engine... >> "..\Run_PWE.bat"
    echo start "" "Pegasus_Wealth_Engine.exe" >> "..\Run_PWE.bat"
    
    echo 📋 Created launcher: Run_PWE.bat
    
) else (
    echo ❌ EXE build failed!
    echo.
    echo 🔧 Troubleshooting:
    echo 1. Check that all dependencies are installed
    echo 2. Ensure you have sufficient disk space (2GB+)
    echo 3. Check PyInstaller log for specific errors
    echo 4. Try running: pip install --upgrade kivy[base] pyinstaller
    echo.
    echo 📋 Common fixes:
    echo • Install Visual C++ Redistributable
    echo • Update PyInstaller: pip install --upgrade pyinstaller
    echo • Check Windows Defender isn't blocking the build
    echo • Run as administrator if needed
    echo.
    pause
    exit /b 1
)

REM Go back to project root
cd ..

echo 🚀 Windows build process completed!

REM Create installation instructions
echo 📋 Creating installation guide...

echo # Pegasus Wealth Engine - Windows Installation Guide > PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo ## 🖥️ Windows Installation Instructions >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo ### Quick Start >> PWE_Windows_Setup.md
echo 1. **Download**: Get `Pegasus_Wealth_Engine.exe` >> PWE_Windows_Setup.md
echo 2. **Run**: Double-click the EXE file to start >> PWE_Windows_Setup.md
echo 3. **Allow**: If Windows shows security warning, click "More info" then "Run anyway" >> PWE_Windows_Setup.md
echo 4. **Enjoy**: The app will start and create necessary files automatically >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo ### Features >> PWE_Windows_Setup.md
echo - ✅ **No Installation Required**: Portable executable >> PWE_Windows_Setup.md
echo - ✅ **Self-Contained**: All dependencies included >> PWE_Windows_Setup.md
echo - ✅ **Local Database**: SQLite database created automatically >> PWE_Windows_Setup.md
echo - ✅ **Voice Control**: Works with Windows microphone >> PWE_Windows_Setup.md
echo - ✅ **Automation Bots**: All money-making bots included >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo ### System Requirements >> PWE_Windows_Setup.md
echo - **OS**: Windows 10/11 (64-bit recommended) >> PWE_Windows_Setup.md
echo - **RAM**: 4GB minimum, 8GB recommended >> PWE_Windows_Setup.md
echo - **Storage**: 500MB free space >> PWE_Windows_Setup.md
echo - **Internet**: Required for API communication >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo ### Troubleshooting >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo **Windows Security Warning** >> PWE_Windows_Setup.md
echo - This is normal for unsigned executables >> PWE_Windows_Setup.md
echo - Click "More info" → "Run anyway" to proceed >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo **Antivirus False Positive** >> PWE_Windows_Setup.md
echo - Some antivirus may flag the EXE as suspicious >> PWE_Windows_Setup.md
echo - Add exception or whitelist the file >> PWE_Windows_Setup.md
echo - This is common with PyInstaller executables >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo **Slow First Startup** >> PWE_Windows_Setup.md
echo - First run may take 30-60 seconds >> PWE_Windows_Setup.md
echo - Subsequent runs will be faster >> PWE_Windows_Setup.md
echo - Windows is loading and caching dependencies >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo ### Configuration >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo **API Settings** >> PWE_Windows_Setup.md
echo - Configure your PWE API URL in the app settings >> PWE_Windows_Setup.md
echo - Default: http://localhost:8000 (for local API) >> PWE_Windows_Setup.md
echo - Update to your deployed API URL if using cloud deployment >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo **Voice Recognition** >> PWE_Windows_Setup.md
echo - Ensure microphone permissions are granted >> PWE_Windows_Setup.md
echo - Test voice input with "Pegasus, earn me money today" >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo **Automation Bots** >> PWE_Windows_Setup.md
echo - Set up email credentials for email bot >> PWE_Windows_Setup.md
echo - Configure Gumroad API for ebook monetization >> PWE_Windows_Setup.md
echo - Install Chrome/ChromeDriver for freelance automation >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo ### Support >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo For issues or questions: >> PWE_Windows_Setup.md
echo 1. Check the console output for error messages >> PWE_Windows_Setup.md
echo 2. Ensure all prerequisites are installed >> PWE_Windows_Setup.md
echo 3. Verify internet connection for API access >> PWE_Windows_Setup.md
echo 4. Update Windows and restart if problems persist >> PWE_Windows_Setup.md
echo. >> PWE_Windows_Setup.md
echo **Happy money-making! 💰** >> PWE_Windows_Setup.md

echo ✅ Created Windows setup guide: PWE_Windows_Setup.md

echo.
echo 🎉 BUILD COMPLETE! 
echo.
echo 📁 Generated Files:
echo   • Pegasus_Wealth_Engine.exe (Main executable)
echo   • Run_PWE.bat (Quick launcher)
echo   • PWE_Windows_Setup.md (Setup guide)
echo.
echo 🚀 Your autonomous money-making app is ready for Windows! 
echo 💰 Double-click the EXE to start making money!
echo.

pause