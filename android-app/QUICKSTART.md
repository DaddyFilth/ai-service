# Quick Start: Android App Setup

This guide will help you get the Android app up and running to connect to your AI service.

## Step 1: Start the AI Service on Your Computer

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Start the AI service:
   ```bash
   cd ai-service
   python api.py
   ```
   
   You should see output like:
   ```
   ======== Running on http://0.0.0.0:8000 ========
   ```

## Step 2: Configure Network Access

### Find Your Computer's IP Address

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (e.g., `192.168.1.100`)

**Mac/Linux:**
```bash
ip addr show
# or
ifconfig
```
Look for `inet` address (e.g., `192.168.1.100`)

### Configure Firewall

Allow incoming connections on port 8000:

**Windows:**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Enter port 8000 → Next
6. Allow the connection → Next
7. Select all profiles → Next
8. Name it "AI Service" → Finish

**macOS:**
```bash
# Firewall should prompt when you start the service
# Click "Allow" when prompted
```

**Linux (UFW):**
```bash
sudo ufw allow 8000
```

### Verify Service is Accessible

From another device on the same network:
```bash
curl http://YOUR_COMPUTER_IP:8000/health
```

Example:
```bash
curl http://192.168.1.100:8000/health
```

You should get a JSON response with service status.

## Step 3: Build the Android APK

On your computer:

```bash
cd ai-service/android-app
./gradlew assembleDebug
```

The APK will be created at:
```
app/build/outputs/apk/debug/app-debug.apk
```

## Step 4: Install the APK on Your Android Device

### Option A: Via USB (ADB)

1. Enable Developer Options on your Android device:
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times

2. Enable USB Debugging:
   - Go to Settings → Developer Options
   - Enable "USB Debugging"

3. Connect your device via USB

4. Install the APK:
   ```bash
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

### Option B: Manual Installation

1. Transfer the APK to your device (via email, Google Drive, USB, etc.)

2. On your Android device:
   - Open the APK file
   - Tap "Install" (you may need to allow installation from unknown sources)

## Step 5: Use the App

1. Open "AI Service Client" on your Android device

2. Enter your computer's IP address and port:
   ```
   http://192.168.1.100:8000
   ```
   (Replace with your actual IP address)

3. Tap "Test Connection"
   - You should see "Connected" in green

4. Fill in call details:
   - Call ID: `test_001`
   - Caller Number: `+1234567890`
   - Called Number: `+0987654321`

5. Tap "Simulate Call"
   - You should see the AI service response

## Troubleshooting

### "Connection failed" Error

1. **Check both devices are on the same WiFi network**
   - Phone and computer must be on the same local network
   
2. **Verify the IP address is correct**
   - Re-check your computer's IP address
   - Make sure you're using `http://` not `https://`
   
3. **Check the service is running**
   ```bash
   curl http://localhost:8000/health
   ```
   
4. **Test from computer browser first**
   - Open `http://YOUR_IP:8000/health` in a browser on your computer
   - If this doesn't work, the issue is with the service or firewall

5. **Check firewall settings**
   - Temporarily disable firewall to test
   - If it works, add proper firewall rule

### "Build failed" Error

1. **Check Java version**
   ```bash
   java -version
   ```
   Should be Java 11 or higher

2. **Clean and rebuild**
   ```bash
   ./gradlew clean
   ./gradlew assembleDebug
   ```

3. **Check internet connection**
   - First build downloads dependencies

### App Crashes

1. Check Android version (must be 7.0 or higher)
2. Check logs:
   ```bash
   adb logcat | grep AIService
   ```

## Example Session

```bash
# On your computer
$ cd ai-service
$ python api.py
Starting up AI Call Service API
AI Call Service API is ready
======== Running on http://0.0.0.0:8000 ========

# In another terminal, check your IP
$ ip addr show | grep inet
    inet 192.168.1.100/24 ...

# On your Android device:
# 1. Open AI Service Client
# 2. Enter: http://192.168.1.100:8000
# 3. Tap "Test Connection" → See "Connected" ✓
# 4. Fill in call details
# 5. Tap "Simulate Call" → See response ✓
```

## Network Configuration for Remote Access

If you want to access the service from outside your local network:

1. **Port Forwarding** (on your router):
   - Forward external port (e.g., 8080) to internal port 8000
   - Point to your computer's local IP

2. **Use Dynamic DNS** (for changing IP addresses):
   - Services like No-IP, DuckDNS, etc.

3. **Security Warning**: 
   - Add authentication before exposing to internet
   - Use HTTPS/SSL for production
   - Consider VPN instead of port forwarding

## Next Steps

- Explore the [full README](README.md) for more details
- Check [BUILD_GUIDE.md](BUILD_GUIDE.md) for advanced build options
- Review the [API documentation](USAGE.md)

## Getting Help

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the logs on both the service and the app
3. Open an issue on GitHub with:
   - Steps to reproduce
   - Error messages
   - Your environment (OS, Android version, etc.)
