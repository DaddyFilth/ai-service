# Multi-User Server Deployment Guide

## Overview

The AI Call Service now supports multiple users with secure authentication. Each user can:
- Register an account with username/email/password
- Login and receive a JWT token or use API key
- Have their own call history tracked
- Access the service from Android mobile devices

## Server Setup

### 1. Install Dependencies

```bash
cd ai-service
pip install -r requirements.txt
```

### 2. Configure Environment

Create/update `.env` file:

```bash
# Asterisk Configuration
ASTERISK_HOST=localhost
ASTERISK_PORT=5060
ASTERISK_USERNAME=ai_service
ASTERISK_PASSWORD=<your-secure-password>

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Service Configuration
SERVICE_HOST=0.0.0.0  # Listen on all interfaces for mobile access
SERVICE_PORT=8000

# JWT Secret (auto-generated if not set)
# Generate with: python3 -c 'import secrets; print(secrets.token_hex(32))'
JWT_SECRET=<your-jwt-secret>
```

### 3. Start the Server

```bash
python3 api.py
```

The server will:
- Create `users.db` SQLite database automatically
- Initialize all tables
- Start listening on `http://0.0.0.0:8000`

### 4. Firewall Configuration

Allow incoming connections on port 8000:

**Linux (ufw):**
```bash
sudo ufw allow 8000/tcp
```

**Linux (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**Windows:**
- Open Windows Defender Firewall
- Add inbound rule for port 8000

## API Usage

### Authentication

#### Register a New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "api_key": "aisk_...",
  "token": "eyJ..."
}
```

#### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "api_key": "aisk_...",
  "token": "eyJ..."
}
```

### Using Authentication

Two methods are supported:

**Method 1: JWT Token (Recommended for mobile apps)**
```bash
curl http://localhost:8000/user/profile \
  -H "Authorization: Bearer <token>"
```

**Method 2: API Key (For server-to-server)**
```bash
curl http://localhost:8000/user/profile \
  -H "X-API-Key: <api_key>"
```

### API Endpoints

#### Public Endpoints (No Auth Required)

- `GET /` - Service information
- `GET /health` - Health check
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login

#### Protected Endpoints (Auth Required)

- `GET /user/profile` - Get current user profile
- `GET /user/calls` - Get user's call history
- `POST /call/incoming` - Submit incoming call (tracked per user)

#### Backward Compatible (Optional Auth)

- `POST /call/incoming` - Can be used with or without authentication
  - With auth: Call is saved to user's history
  - Without auth: Call is processed but not saved to any user

### Call History

Get your call history:
```bash
curl http://localhost:8000/user/calls?limit=10 \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "user_id": 1,
  "username": "john",
  "total_calls": 2,
  "calls": [
    {
      "id": 1,
      "call_id": "test_001",
      "caller_number": "+1234567890",
      "called_number": "+0987654321",
      "timestamp": "2026-02-04T12:00:00+00:00",
      "action": "forward",
      "message": "Forwarding call to sales",
      "status": "completed"
    }
  ]
}
```

## Testing Multi-User Support

Use the included test script:

```bash
python3 test_multiuser.py
```

This will:
1. Register two test users
2. Login with both users
3. Simulate calls for each user
4. Retrieve call history
5. Test authentication

## Android App Integration

### Required Changes to Android App

The Android app needs to be updated to support user authentication. Here's what needs to be added:

#### 1. New Screens

**LoginActivity.kt**
- Username/email and password fields
- Login button
- Link to registration screen
- "Remember me" option

**RegisterActivity.kt**
- Username, email, password fields
- Password confirmation field
- Register button
- Link back to login

#### 2. Secure Storage

Store credentials securely using Android Encrypted SharedPreferences:

```kotlin
// Store token
val sharedPreferences = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

sharedPreferences.edit()
    .putString("jwt_token", token)
    .putString("api_key", apiKey)
    .apply()
```

#### 3. Update API Client

Add authentication headers to all requests:

```kotlin
// In ApiClient.kt
private fun getAuthInterceptor(): Interceptor {
    return Interceptor { chain ->
        val token = getStoredToken()
        val request = if (token != null) {
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }
        chain.proceed(request)
    }
}
```

#### 4. New API Endpoints

Add to `AIServiceApi.kt`:

```kotlin
@POST("auth/register")
suspend fun register(@Body request: RegisterRequest): Response<UserResponse>

@POST("auth/login")
suspend fun login(@Body request: LoginRequest): Response<UserResponse>

@GET("user/profile")
suspend fun getProfile(): Response<UserProfile>

@GET("user/calls")
suspend fun getCallHistory(@Query("limit") limit: Int = 50): Response<CallHistoryResponse>
```

#### 5. Update MainActivity

- Check if user is logged in on startup
- Redirect to login if not authenticated
- Show user profile information
- Add logout option
- Display user-specific call history from server

### Building the Updated APK

Once Android app changes are complete:

```bash
cd android-app
./gradlew assembleRelease
```

The APK will be at:
```
android-app/app/build/outputs/apk/release/app-release.apk
```

## Production Deployment

### 1. Use HTTPS

For production, use a reverse proxy with SSL:

**Nginx Configuration:**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Use Process Manager

Use systemd to manage the service:

```ini
[Unit]
Description=AI Call Service
After=network.target

[Service]
Type=simple
User=aiservice
WorkingDirectory=/opt/ai-service
Environment="PATH=/opt/ai-service/venv/bin"
ExecStart=/opt/ai-service/venv/bin/python3 api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Database Backups

Backup the user database regularly:

```bash
# Backup
sqlite3 users.db ".backup '/backup/users-$(date +%Y%m%d).db'"

# Restore
sqlite3 users.db ".restore '/backup/users-20260204.db'"
```

### 4. Security Best Practices

- Set strong JWT_SECRET in production
- Use HTTPS only for mobile connections
- Regularly update dependencies
- Monitor failed login attempts
- Enable rate limiting (use nginx limit_req)
- Regular database backups

## Monitoring

### Check Active Users

```bash
sqlite3 users.db "SELECT COUNT(*) FROM users WHERE is_active = 1;"
```

### View Recent Calls

```bash
sqlite3 users.db "SELECT * FROM call_history ORDER BY timestamp DESC LIMIT 10;"
```

### Check User Activity

```bash
sqlite3 users.db "SELECT username, last_login FROM users ORDER BY last_login DESC;"
```

## Troubleshooting

### Database Locked Error

If you see "database is locked":
```bash
# Check for hung connections
lsof users.db

# Restart the service
systemctl restart ai-service
```

### Authentication Failures

1. Check JWT_SECRET is consistent
2. Verify password meets requirements (12+ chars, no weak patterns)
3. Check token hasn't expired (24 hour default)
4. Verify API key format: starts with "aisk_"

### Mobile App Can't Connect

1. Verify server is listening on 0.0.0.0:8000
2. Check firewall allows port 8000
3. Use server's LAN IP address (not localhost)
4. Test from server: `curl http://0.0.0.0:8000/health`
5. Test from network: `curl http://<server-ip>:8000/health`

## Support

For issues:
1. Check server logs
2. Test with `test_multiuser.py`
3. Verify database with sqlite3
4. Check firewall and network settings
