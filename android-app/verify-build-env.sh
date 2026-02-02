#!/bin/bash
# Pre-build verification script for Android app

echo "==================================="
echo "Android App Build Verification"
echo "==================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Check Java
echo -n "Checking Java installation... "
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    JAVA_MAJOR=$(echo $JAVA_VERSION | cut -d'.' -f1)
    if [ "$JAVA_MAJOR" -ge 11 ]; then
        echo -e "${GREEN}✓${NC} Java $JAVA_VERSION"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} Java $JAVA_VERSION (need 11+)"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
else
    echo -e "${RED}✗${NC} Java not found"
    echo "   Install Java 11+ from https://adoptium.net/"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check JAVA_HOME
echo -n "Checking JAVA_HOME... "
if [ -n "$JAVA_HOME" ]; then
    echo -e "${GREEN}✓${NC} $JAVA_HOME"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} Not set (optional, auto-detected)"
fi

# Check Gradle wrapper
echo -n "Checking Gradle wrapper... "
if [ -f "gradlew" ]; then
    if [ -x "gradlew" ]; then
        echo -e "${GREEN}✓${NC} Found and executable"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠${NC} Found but not executable, fixing..."
        chmod +x gradlew
        echo -e "${GREEN}✓${NC} Fixed"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    fi
else
    echo -e "${RED}✗${NC} gradlew not found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check gradle wrapper jar
echo -n "Checking Gradle wrapper JAR... "
if [ -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    echo -e "${GREEN}✓${NC} Found"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} gradle-wrapper.jar not found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check build.gradle
echo -n "Checking build.gradle... "
if [ -f "build.gradle" ]; then
    echo -e "${GREEN}✓${NC} Found"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} build.gradle not found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check app module
echo -n "Checking app module... "
if [ -d "app" ]; then
    if [ -f "app/build.gradle" ]; then
        echo -e "${GREEN}✓${NC} Found"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} app/build.gradle not found"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
else
    echo -e "${RED}✗${NC} app directory not found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check source files
echo -n "Checking source files... "
SOURCE_DIR="app/src/main/java/com/aiservice/client"
if [ -d "$SOURCE_DIR" ]; then
    KOTLIN_FILES=$(find "$SOURCE_DIR" -name "*.kt" | wc -l)
    if [ "$KOTLIN_FILES" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Found $KOTLIN_FILES Kotlin files"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} No Kotlin files found"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
else
    echo -e "${RED}✗${NC} Source directory not found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check AndroidManifest.xml
echo -n "Checking AndroidManifest.xml... "
if [ -f "app/src/main/AndroidManifest.xml" ]; then
    echo -e "${GREEN}✓${NC} Found"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} AndroidManifest.xml not found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check internet connection
echo -n "Checking internet connection... "
if ping -c 1 google.com &> /dev/null || ping -c 1 8.8.8.8 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Connected"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠${NC} No connection (needed for first build)"
fi

# Check disk space
echo -n "Checking disk space... "
if command -v df &> /dev/null; then
    AVAILABLE_MB=$(df -m . | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_MB" -gt 1000 ]; then
        echo -e "${GREEN}✓${NC} ${AVAILABLE_MB}MB available"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠${NC} Only ${AVAILABLE_MB}MB available (need ~1GB)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Could not check"
fi

# Optional checks
echo ""
echo "Optional Tools:"

# Check Android SDK
echo -n "  Android SDK (ANDROID_HOME)... "
if [ -n "$ANDROID_HOME" ]; then
    echo -e "${GREEN}✓${NC} $ANDROID_HOME"
else
    echo -e "${YELLOW}○${NC} Not set (Gradle will download)"
fi

# Check ADB
echo -n "  ADB for installation... "
if command -v adb &> /dev/null; then
    ADB_VERSION=$(adb version | head -n 1)
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}○${NC} Not found (optional, for USB install)"
fi

# Summary
echo ""
echo "==================================="
echo "Summary:"
echo -e "  ${GREEN}✓${NC} Passed: $CHECKS_PASSED"
if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "  ${RED}✗${NC} Failed: $CHECKS_FAILED"
fi
echo "==================================="
echo ""

# Recommendation
if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    echo ""
    echo "You're ready to build the APK:"
    echo "  ./gradlew assembleDebug"
    echo ""
    echo "The APK will be created at:"
    echo "  app/build/outputs/apk/debug/app-debug.apk"
    exit 0
else
    echo -e "${RED}Some checks failed.${NC}"
    echo ""
    echo "Please resolve the issues above before building."
    echo "See BUILD_GUIDE.md for more information."
    exit 1
fi
