# Android App - Connect Your Phone to AI Service

An Android application is available to connect your Android device to the AI Call Service running on your computer.

## Quick Start

1. **On your computer:**
   ```bash
   cd ai-service
   python api.py
   ```

2. **Build the Android app:**
   ```bash
   cd android-app
   ./gradlew assembleDebug
   ```

3. **Install on your Android device:**
   ```bash
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

4. **Connect:**
   - Open the app on your Android device
   - Enter your computer's IP: `http://192.168.1.100:8000`
   - Test the connection
   - Simulate calls

## Documentation

Full documentation is available in the `android-app/` directory:

- **[android-app/README.md](android-app/README.md)** - Overview and features
- **[android-app/QUICKSTART.md](android-app/QUICKSTART.md)** - Step-by-step setup guide
- **[android-app/BUILD_GUIDE.md](android-app/BUILD_GUIDE.md)** - Detailed build instructions
- **[android-app/ARCHITECTURE.md](android-app/ARCHITECTURE.md)** - Technical architecture
- **[android-app/TROUBLESHOOTING.md](android-app/TROUBLESHOOTING.md)** - Common issues and solutions
- **[android-app/SUMMARY.md](android-app/SUMMARY.md)** - Implementation summary

## Features

- ✅ Test connection to AI service
- ✅ Simulate incoming calls
- ✅ View AI service responses
- ✅ Connection health monitoring
- ✅ Material Design UI

## Requirements

- Android 7.0 (API 24) or higher
- Computer and Android device on same WiFi network
- AI Service running on computer
- Java 11+ for building

## Support

See the [troubleshooting guide](android-app/TROUBLESHOOTING.md) for help with common issues.
