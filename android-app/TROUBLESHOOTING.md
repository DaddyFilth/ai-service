# Troubleshooting Guide

Common issues and solutions for the Android AI Service Client app.

## Table of Contents
- [Connection Issues](#connection-issues)
- [Build Issues](#build-issues)
- [Installation Issues](#installation-issues)
- [Runtime Issues](#runtime-issues)
- [Network Issues](#network-issues)

---

## Connection Issues

### Issue: "Connection failed: Failed to connect"

**Possible Causes:**
1. Service not running on computer
2. Wrong IP address
3. Firewall blocking connection
4. Not on same network

**Solutions:**

1. **Verify service is running:**
   ```bash
   # On your computer
   curl http://localhost:8000/health
   ```
   Should return JSON response. If not, start the service:
   ```bash
   python api.py
   ```

2. **Verify IP address:**
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   # or
   ip addr show
   ```
   Use the correct IPv4 address (e.g., 192.168.1.100)

3. **Test from computer first:**
   ```bash
   curl http://YOUR_COMPUTER_IP:8000/health
   ```
   If this fails, it's a firewall/network issue on computer.

4. **Check firewall:**
   - Windows: Allow port 8000 in Windows Firewall
   - Mac: Allow api.py in System Preferences → Security
   - Linux: `sudo ufw allow 8000`

5. **Verify same network:**
   - Both devices must be on same WiFi network
   - Check WiFi SSID on both devices

### Issue: "Connection timeout"

**Solutions:**
- Increase timeout in app (requires code change)
- Check network speed
- Restart router
- Move devices closer to router

### Issue: "Unknown host exception"

**Solutions:**
- Check URL format: `http://192.168.1.100:8000` (not `https://`)
- Don't use localhost or 127.0.0.1 (that's the Android device itself)
- Don't include trailing slash
- Check for typos in IP address

### Issue: "SSL/TLS error" or "Cleartext HTTP not permitted"

**Solutions:**
- Verify using `http://` not `https://`
- App already has `usesCleartextTraffic=true` in manifest
- If building custom version, ensure this setting is present

---

## Build Issues

### Issue: "JAVA_HOME not set"

**Solutions:**
1. Install JDK 11 or higher
2. Set JAVA_HOME:
   ```bash
   # Linux/Mac
   export JAVA_HOME=/path/to/jdk
   
   # Windows
   set JAVA_HOME=C:\Path\To\JDK
   ```

### Issue: "Could not resolve dependencies"

**Solutions:**
1. Check internet connection
2. Clear Gradle cache:
   ```bash
   ./gradlew clean
   rm -rf ~/.gradle/caches
   ```
3. Retry with:
   ```bash
   ./gradlew assembleDebug --refresh-dependencies
   ```

### Issue: "Could not download Gradle"

**Solutions:**
1. Check internet connection
2. Download manually from https://gradle.org
3. Use local Gradle installation:
   ```bash
   gradle assembleDebug
   ```

### Issue: "Android SDK not found"

**Solutions:**
1. Install Android Studio (includes SDK)
2. Or set ANDROID_HOME:
   ```bash
   export ANDROID_HOME=/path/to/android/sdk
   ```
3. Or let Gradle download SDK automatically (first build)

### Issue: "Build failed with compilation errors"

**Solutions:**
1. Check Kotlin version compatibility
2. Update build tools:
   ```bash
   ./gradlew clean assembleDebug
   ```
3. Check for syntax errors in code
4. Review full error log:
   ```bash
   ./gradlew assembleDebug --stacktrace
   ```

---

## Installation Issues

### Issue: "App not installed" or "Installation blocked"

**Solutions:**
1. Enable "Install from unknown sources":
   - Settings → Security → Unknown sources → Enable
   - Or Settings → Apps → Special access → Install unknown apps

2. Uninstall old version first:
   ```bash
   adb uninstall com.aiservice.client
   ```

3. Check storage space (need at least 50 MB free)

4. Try installing via ADB:
   ```bash
   adb install -r app/build/outputs/apk/debug/app-debug.apk
   ```

### Issue: "Parse error" or "Invalid APK"

**Solutions:**
1. Re-download/transfer APK (may be corrupted)
2. Rebuild APK:
   ```bash
   ./gradlew clean assembleDebug
   ```
3. Check Android version (need 7.0+)

### Issue: ADB device not found

**Solutions:**
1. Enable USB debugging on Android device
2. Reconnect USB cable
3. Check ADB connection:
   ```bash
   adb devices
   ```
4. Install/update ADB drivers (Windows)
5. Authorize device when prompted

---

## Runtime Issues

### Issue: App crashes on launch

**Solutions:**
1. Check Android version (minimum 7.0 / API 24)
2. Clear app data:
   - Settings → Apps → AI Service Client → Clear Data
3. Reinstall app
4. Check logs:
   ```bash
   adb logcat | grep -i "aiservice"
   ```

### Issue: "No response from server"

**Solutions:**
1. Check service is running
2. Verify URL is correct
3. Test health endpoint first
4. Check logs on server side
5. Restart service:
   ```bash
   # Stop service (Ctrl+C)
   python api.py
   ```

### Issue: Response shows "error" status

**Solutions:**
1. Check server logs for errors
2. Verify Ollama is running:
   ```bash
   ollama list
   ollama serve
   ```
3. Check AI service configuration (.env file)
4. Review error message in response

---

## Network Issues

### Issue: Service accessible from computer but not from phone

**Solutions:**
1. **Check isolation:**
   - Some routers have "AP isolation" or "client isolation"
   - Disable this in router settings
   
2. **Check subnet:**
   - Both devices should be on same subnet (e.g., 192.168.1.x)
   
3. **Check VPN:**
   - Disable VPN on phone or computer
   - VPN can route traffic differently

4. **Try mobile hotspot:**
   - Connect computer to phone's hotspot
   - Use hotspot IP address
   - Tests if router is the issue

### Issue: Service works on WiFi but not mobile data

**Expected Behavior:**
- Service only accessible on local network
- Won't work on mobile data unless you set up port forwarding

**Solutions for remote access:**
1. Set up port forwarding on router
2. Use dynamic DNS service
3. Use VPN (recommended for security)
4. Use ngrok or similar tunneling service (development only)

### Issue: Intermittent connection drops

**Solutions:**
1. Check WiFi signal strength
2. Move closer to router
3. Restart router
4. Check for interference (other WiFi networks, devices)
5. Use 5GHz WiFi band if available

---

## Debugging Tips

### Enable Verbose Logging

**Android App:**
Already enabled in debug builds via OkHttp logging interceptor.

**Server:**
```python
# In config.py or api.py
logging.basicConfig(level=logging.DEBUG)
```

### Capture Network Traffic

**Android:**
1. Install HTTP Toolkit on computer
2. Follow Android setup instructions
3. Capture traffic from AI Service Client app

**Computer:**
```bash
# Monitor port 8000
sudo tcpdump -i any port 8000 -A
```

### Check Logs

**Android:**
```bash
adb logcat | grep -E "(AIService|Retrofit|OkHttp)"
```

**Server:**
Check terminal output where `python api.py` is running

### Test API Manually

**Using curl:**
```bash
# Health check
curl http://YOUR_IP:8000/health

# Simulate call
curl -X POST http://YOUR_IP:8000/call/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_001",
    "caller_number": "+1234567890",
    "called_number": "+0987654321"
  }'
```

**Using browser:**
Navigate to `http://YOUR_IP:8000/health`

---

## Getting Help

If none of these solutions work:

1. **Gather information:**
   - Android version
   - Computer OS
   - Error messages
   - Steps to reproduce
   - Logs (both app and server)

2. **Check existing issues:**
   - GitHub Issues page
   - Search for similar problems

3. **Open a new issue:**
   - Include all information from step 1
   - Include screenshots if applicable
   - Attach relevant log files

4. **Contact:**
   - Open issue on GitHub
   - Include "Android App" in the title

---

## Common Error Messages

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| "Connection refused" | Service not running or wrong port | Start service, check port |
| "No route to host" | Network issue or firewall | Check firewall, network |
| "Unknown host" | Invalid URL/IP | Check URL format |
| "Timeout" | Slow network or service not responding | Check network, restart service |
| "401 Unauthorized" | Authentication required | Add auth (not implemented yet) |
| "404 Not Found" | Wrong endpoint | Check URL path |
| "500 Internal Server Error" | Server error | Check server logs |

---

## Prevention Tips

1. **Save working configuration:**
   - Note working IP address
   - Save firewall rules
   - Document network setup

2. **Regular testing:**
   - Test after router changes
   - Test after OS updates
   - Test after firewall changes

3. **Network stability:**
   - Use wired connection for computer (if possible)
   - Keep devices close to router
   - Minimize WiFi interference

4. **Monitoring:**
   - Keep server logs
   - Monitor app logs during development
   - Set up health check monitoring
