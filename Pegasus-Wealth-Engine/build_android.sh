#!/bin/bash

# Pegasus Wealth Engine - Android APK Build Script
# Builds the PWE Kivy app into an Android APK using Buildozer

echo "🚀 Starting Android APK build for Pegasus Wealth Engine..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "pwe_app" ]; then
    echo -e "${RED}❌ Error: pwe_app directory not found. Please run this script from the Pegasus-Wealth-Engine root directory.${NC}"
    exit 1
fi

echo -e "${BLUE}📱 Building Android APK for PWE App...${NC}"

# Navigate to the app directory
cd pwe_app

# Check if buildozer.spec exists, if not create it
if [ ! -f "buildozer.spec" ]; then
    echo -e "${YELLOW}⚙️ Creating buildozer.spec configuration...${NC}"
    
    # Initialize buildozer
    buildozer init
    
    # Customize buildozer.spec for PWE
    cat > buildozer.spec << 'EOF'
[app]

# (str) Title of your application
title = Pegasus Wealth Engine

# (str) Package name
package.name = pegasus_wealth_engine

# (str) Package domain (needed for android/ios packaging)
package.domain = com.pwe.app

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt,md

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.1.0,kivymd,requests,sqlite3,schedule,pillow,certifi,plyer,numpy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, sensorLandscape, portrait, sensorPortrait, all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,RECORD_AUDIO

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android SDK version to use
android.sdk = 31

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
#android.service_class_name = org.kivy.android.PythonService

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
# android.enable_androidx requires android.api >= 28
android.enable_androidx = True

# (str) Android gradle dependencies to add
#android.gradle_dependencies =

# (str) Android gradle repositories to add (may be needed when gradle_dependencies declares a repository not in the default list)
#android.gradle_repositories =

# (str) Java classes to add to the project (can be a list separated by comma)
#android.java_classes =

# (str) Python packages to add as gradle dependencies, each package name
# should be the first letters of the package name (e.g. 'pil' for 'Pillow')
#android.gradle_python_packages =

# (str) Gradle repositories to add for gradle dependencies (may be needed when gradle_dependencies declares a repository not in the default list)
#android.gradle_repositories =

# (str) python modules to add to the requirements (can be a list separated by comma)
#android.python_packages =

# (str) python modules to add to the gradle dependencies (can be a list separated by comma)
#android.gradle_python_packages =

# (str) Arch of the application, you can use all, armeabi-v7a, arm64-v8a or x86
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

EOF

    echo -e "${GREEN}✅ buildozer.spec created successfully${NC}"
fi

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo -e "${YELLOW}⚠️ Buildozer not found. Installing...${NC}"
    
    # Check if we're on Android (Termux)
    if [ -n "$TERMUX_VERSION" ]; then
        echo -e "${BLUE}📱 Detected Termux environment...${NC}"
        
        # Termux-specific installation
        pkg update -y
        pkg install -y python python-dev python-pip build-essential libffi-dev openssl-dev
        pkg install -y git zip unzip autoconf automake libtool pkg-config
        pkg install -y openjdk-17
        
        # Install buildozer
        pip install --upgrade pip
        pip install buildozer
        pip install cython
        
        # Set JAVA_HOME for Termux
        export JAVA_HOME=$PREFIX/opt/openjdk
        
    else
        echo -e "${BLUE}🖥️ Detected Linux environment...${NC}"
        
        # Linux installation
        sudo apt-get update
        sudo apt-get install -y python3-pip python3-dev build-essential
        sudo apt-get install -y git zip unzip autoconf automake libtool pkg-config
        sudo apt-get install -y openjdk-11-jdk
        
        # Install buildozer
        pip3 install --upgrade pip
        pip3 install buildozer
        pip3 install cython
        
        # Set JAVA_HOME for Linux
        export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    fi
    
    echo -e "${GREEN}✅ Buildozer installed successfully${NC}"
fi

# Install additional dependencies for PWE
echo -e "${YELLOW}📦 Installing PWE dependencies...${NC}"
pip install -r requirements.txt

# Clean previous builds
echo -e "${YELLOW}🧹 Cleaning previous builds...${NC}"
buildozer android clean

# Build the APK
echo -e "${BLUE}🔨 Building Android APK... (This may take 10-30 minutes)${NC}"
echo -e "${YELLOW}⏳ Please be patient, downloading and compiling dependencies...${NC}"

# Set environment variables
export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Build APK in debug mode (faster)
buildozer android debug

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ APK build completed successfully!${NC}"
    
    # Find the generated APK
    APK_FILE=$(find bin -name "*.apk" -type f | head -1)
    
    if [ -n "$APK_FILE" ]; then
        echo -e "${GREEN}📱 APK file created: $APK_FILE${NC}"
        
        # Get file size
        APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
        echo -e "${BLUE}📊 APK size: $APK_SIZE${NC}"
        
        # Move APK to project root for easy access
        cp "$APK_FILE" "../pegasus_wealth_engine.apk"
        echo -e "${GREEN}📋 APK copied to: ../pegasus_wealth_engine.apk${NC}"
        
        echo ""
        echo -e "${GREEN}🎉 SUCCESS! Your Pegasus Wealth Engine APK is ready!${NC}"
        echo ""
        echo -e "${BLUE}📱 Installation Instructions:${NC}"
        echo "1. Transfer the APK to your Android device"
        echo "2. Enable 'Install from Unknown Sources' in Android settings"
        echo "3. Open the APK file to install"
        echo "4. Grant necessary permissions when prompted"
        echo ""
        echo -e "${YELLOW}⚠️ Note: This is a debug APK. For production release, use:${NC}"
        echo "   buildozer android release"
        echo ""
        
    else
        echo -e "${RED}❌ APK file not found in bin directory${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ APK build failed!${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Troubleshooting:${NC}"
    echo "1. Check that all dependencies are installed"
    echo "2. Ensure you have sufficient disk space (5GB+)"
    echo "3. Check buildozer log for specific errors"
    echo "4. Try: buildozer android clean && buildozer android debug"
    echo ""
    echo -e "${BLUE}📋 Common fixes:${NC}"
    echo "• Install missing system packages"
    echo "• Update buildozer: pip install --upgrade buildozer"
    echo "• Check Java version: java -version"
    echo "• Ensure Android SDK is properly configured"
    echo ""
    exit 1
fi

# Go back to project root
cd ..

echo -e "${GREEN}🚀 Android build process completed!${NC}"

# Optional: Create installation script
cat > install_android.sh << 'EOF'
#!/bin/bash

# PWE Android Installation Helper
echo "📱 Installing Pegasus Wealth Engine on Android device..."

# Check if ADB is available
if command -v adb &> /dev/null; then
    echo "📲 ADB found. Installing via USB debugging..."
    
    # Check if device is connected
    if adb devices | grep -q "device$"; then
        echo "🔗 Android device detected"
        
        # Install APK
        adb install -r pegasus_wealth_engine.apk
        
        if [ $? -eq 0 ]; then
            echo "✅ PWE installed successfully!"
            echo "🚀 You can now find 'Pegasus Wealth Engine' in your app drawer"
        else
            echo "❌ Installation failed. Please install manually."
        fi
    else
        echo "⚠️ No Android device detected via ADB"
        echo "📋 Manual installation:"
        echo "1. Transfer pegasus_wealth_engine.apk to your phone"
        echo "2. Enable 'Install from Unknown Sources'"
        echo "3. Tap the APK file to install"
    fi
else
    echo "📋 Manual installation required:"
    echo "1. Transfer pegasus_wealth_engine.apk to your Android device"
    echo "2. Go to Settings > Security > Enable 'Unknown Sources'"
    echo "3. Open file manager and tap the APK to install"
    echo "4. Grant permissions when prompted"
    echo ""
    echo "🔗 The APK file is: pegasus_wealth_engine.apk"
fi
EOF

chmod +x install_android.sh

echo -e "${BLUE}📋 Created installation helper: install_android.sh${NC}"
echo -e "${GREEN}✨ Build complete! Your autonomous money-making app is ready for Android! 🎉${NC}"