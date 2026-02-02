# Building the Android APK

Due to network restrictions in some environments, you may need to build the APK on your local machine. This guide explains how to do that.

## Prerequisites

1. **Java Development Kit (JDK) 11 or higher**
   - Download from: https://adoptium.net/ or https://www.oracle.com/java/technologies/downloads/
   - Verify installation: `java -version`

2. **Android SDK** (Optional - Gradle will download it automatically)
   - If you have Android Studio installed, you already have it
   - Otherwise, set `ANDROID_HOME` environment variable if you have SDK installed separately

## Building on Your Local Machine

### Step 1: Clone the Repository

```bash
git clone https://github.com/DaddyFilth/ai-service.git
cd ai-service/android-app
```

### Step 2: Build the APK

**On Linux/Mac:**
```bash
./gradlew assembleDebug
```

**On Windows:**
```cmd
gradlew.bat assembleDebug
```

The build process will:
1. Download Gradle (if needed)
2. Download Android SDK components (if needed)
3. Download dependencies
4. Compile the app
5. Generate the APK

### Step 3: Locate the APK

The APK will be created at:
```
app/build/outputs/apk/debug/app-debug.apk
```

## Build Output

After a successful build, you'll see:
```
BUILD SUCCESSFUL in XXs
```

## Troubleshooting

### Problem: "JAVA_HOME not set"

**Solution:** Set the JAVA_HOME environment variable:

Linux/Mac:
```bash
export JAVA_HOME=/path/to/your/jdk
```

Windows:
```cmd
set JAVA_HOME=C:\Path\To\Your\JDK
```

### Problem: "Could not resolve dependencies"

**Solution:** Check your internet connection and try again:
```bash
./gradlew assembleDebug --refresh-dependencies
```

### Problem: Build is slow

**Solution:** First build downloads everything - it's normal. Subsequent builds will be much faster.

## Release Build (Signed APK)

For a release version that can be published:

1. Create a keystore:
```bash
keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

2. Create `android-app/keystore.properties`:
```properties
storePassword=your_store_password
keyPassword=your_key_password
keyAlias=my-key-alias
storeFile=../my-release-key.keystore
```

3. Update `app/build.gradle` to include signing config

4. Build release APK:
```bash
./gradlew assembleRelease
```

## Alternative: Build with Android Studio

1. Install [Android Studio](https://developer.android.com/studio)
2. Open the `android-app` folder as a project
3. Click **Build → Build Bundle(s) / APK(s) → Build APK(s)**
4. Find the APK in `app/build/outputs/apk/debug/`

## Testing the APK

### Install via USB (ADB)

1. Enable USB debugging on your Android device
2. Connect device to computer via USB
3. Install the APK:
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Install Manually

1. Transfer the APK to your Android device (via email, cloud storage, USB, etc.)
2. Open the APK file on your device
3. Enable "Install from unknown sources" if prompted
4. Tap Install

## Expected Build Time

- First build: 2-5 minutes (downloads dependencies)
- Subsequent builds: 30 seconds - 1 minute

## Build Artifacts Size

- APK size: Approximately 5-8 MB
- Build artifacts: ~200-300 MB (gradle cache, dependencies)

## Cleaning Build

To clean all build artifacts:
```bash
./gradlew clean
```

## Getting Help

If you encounter issues:

1. Check Java version: `java -version` (should be 11+)
2. Run with stacktrace: `./gradlew assembleDebug --stacktrace`
3. Run with debug info: `./gradlew assembleDebug --debug`
4. Clean and rebuild: `./gradlew clean assembleDebug`

## Build Configuration

The app is configured to:
- Minimum Android version: 7.0 (API 24)
- Target Android version: 13 (API 33)
- Build tools: Gradle 8.0, Android Gradle Plugin 7.4.2
- Language: Kotlin
- Dependencies: Retrofit, OkHttp, Material Design, Coroutines
