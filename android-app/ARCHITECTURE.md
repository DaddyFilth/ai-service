# Android App Architecture

## Connection Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Local Network (WiFi)                     │
│                                                               │
│  ┌──────────────────────┐         ┌──────────────────────┐  │
│  │   Android Device     │         │   Computer           │  │
│  │                      │         │                      │  │
│  │  ┌────────────────┐  │         │  ┌────────────────┐  │  │
│  │  │ AI Service     │  │         │  │ Python         │  │  │
│  │  │ Client App     │  │  HTTP   │  │ API Server     │  │  │
│  │  │                │──┼────────→│  │ (api.py)       │  │  │
│  │  │ - Test Health  │  │  :8000  │  │                │  │  │
│  │  │ - Simulate     │  │  JSON   │  │ - /health      │  │  │
│  │  │   Calls        │  │←────────┼──│ - /call/       │  │  │
│  │  │ - View Results │  │         │  │   incoming     │  │  │
│  │  └────────────────┘  │         │  └────────────────┘  │  │
│  │                      │         │          ↓           │  │
│  │  IP: Dynamic         │         │  ┌────────────────┐  │  │
│  │  Port: N/A           │         │  │ Ollama Service │  │  │
│  └──────────────────────┘         │  │ (AI Engine)    │  │  │
│                                    │  │                │  │  │
│                                    │  │ :11434         │  │  │
│                                    │  └────────────────┘  │  │
│                                    │                      │  │
│                                    │  IP: 192.168.1.100   │  │
│                                    │  Port: 8000          │  │
│                                    └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Android App (Client)

```
MainActivity
    ├── UI Layer (activity_main.xml)
    │   ├── Server URL Input
    │   ├── Connection Test Button
    │   ├── Call Simulation Form
    │   └── Response Display
    │
    ├── Network Layer
    │   ├── ApiClient (Retrofit + OkHttp)
    │   ├── AIServiceApi (REST API Interface)
    │   └── Models (Data classes)
    │
    └── Business Logic
        ├── Connection Management
        ├── Request/Response Handling
        └── Error Handling
```

### API Endpoints

```
GET  /              → Root endpoint (service info)
GET  /health        → Health check (component status)
POST /call/incoming → Simulate incoming call
GET  /call/{id}/status → Get call status
```

### Request/Response Flow

```
User Action → UI → ViewModel → ApiClient → Network → Server
                                                         ↓
User Display ← UI ← ViewModel ← Response ← Network ← Server
```

## Data Models

### CallRequest (Client → Server)
```json
{
  "call_id": "test_001",
  "caller_number": "+1234567890",
  "called_number": "+0987654321",
  "timestamp": "2026-02-02T16:00:00Z",
  "channel": "Android-App"
}
```

### CallResponse (Server → Client)
```json
{
  "status": "success",
  "call_id": "test_001",
  "action": "forward|voicemail|ask_question",
  "message": "Call processed successfully"
}
```

### HealthResponse
```json
{
  "status": "healthy",
  "components": {
    "sip": true,
    "stt": true,
    "decision_engine": true,
    "action_router": true
  }
}
```

## Network Configuration

### Requirements
- Both devices on same network (WiFi/LAN)
- Computer firewall allows port 8000
- Service running on 0.0.0.0:8000 (all interfaces)

### Security Considerations
- **Development**: Uses cleartext HTTP (usesCleartextTraffic=true)
- **Production**: Should use HTTPS with valid certificate
- **Authentication**: Currently none - add before production use

### Permissions (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

## Technology Stack

### Android App
- **Language**: Kotlin
- **Minimum SDK**: 24 (Android 7.0)
- **Target SDK**: 33 (Android 13)
- **Build System**: Gradle 8.0
- **UI**: Material Design Components
- **Networking**: Retrofit 2.9.0 + OkHttp 4.11.0
- **Async**: Kotlin Coroutines
- **JSON**: Gson

### Server (Python)
- **Framework**: aiohttp (async web server)
- **Port**: 8000 (configurable)
- **Protocol**: HTTP/1.1
- **Data Format**: JSON
- **AI Engine**: Ollama (llama2 model)

## Error Handling

### Connection Errors
```
Network Error → Display error toast
              → Update connection status to "Not Connected"
              → Show error details in response text
```

### Server Errors (4xx, 5xx)
```
HTTP Error → Parse error body
           → Display error message
           → Show HTTP status code
```

### Validation Errors
```
Empty Fields → Show "Please fill in all fields"
Invalid URL → Show "Please enter a valid URL"
```

## Testing Scenarios

1. **Health Check**
   - Input: Server URL
   - Action: Click "Test Connection"
   - Expected: "Connected" status, component info displayed

2. **Call Simulation**
   - Input: Call details (ID, numbers)
   - Action: Click "Simulate Call"
   - Expected: Response with action and message

3. **Error Cases**
   - No network: "Connection failed"
   - Wrong URL: "Connection failed"
   - Server down: "Connection timeout"
   - Invalid data: Validation error

## Build Process

```
Source Code (.kt, .xml)
    ↓
Kotlin Compiler
    ↓
Java Bytecode (.class)
    ↓
D8 Dex Compiler
    ↓
DEX Files (.dex)
    ↓
Android Asset Packaging Tool (AAPT2)
    ↓
APK Package (.apk)
    ↓
Zipalign & Sign (if release)
    ↓
Installable APK
```

## Future Enhancements

- [ ] Save server URL preference
- [ ] Connection history
- [ ] Call history log
- [ ] Real-time call status updates
- [ ] Push notifications for incoming calls
- [ ] Audio recording/playback
- [ ] Video call support
- [ ] Multi-language UI
- [ ] Dark/light theme
- [ ] Settings screen
