# Android App Update Guide for Multi-User Support

## Overview

This guide outlines the changes needed to update the Android app to support the new multi-user server functionality.

## Summary of Required Changes

### 1. Add Authentication Screens

#### New Files to Create:
- `LoginActivity.kt` - User login screen
- `RegisterActivity.kt` - User registration screen
- `activity_login.xml` - Login layout
- `activity_register.xml` - Registration layout

### 2. Update Dependencies

Add to `app/build.gradle`:

```gradle
dependencies {
    // Existing dependencies...
    
    // Security for encrypted storage
    implementation 'androidx.security:security-crypto:1.1.0-alpha06'
    
    // ViewModel and LiveData
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.7.0'
}
```

### 3. Update API Models

Add to `Models.kt`:

```kotlin
// Registration request
data class RegisterRequest(
    val username: String,
    val email: String,
    val password: String
)

// Login request
data class LoginRequest(
    val username: String,
    val password: String
)

// User response
data class UserResponse(
    val id: Int,
    val username: String,
    val email: String,
    val api_key: String,
    val token: String?
)

// Call history response
data class CallHistoryResponse(
    val user_id: Int,
    val username: String,
    val total_calls: Int,
    val calls: List<CallHistoryItem>
)

data class CallHistoryItem(
    val id: Int,
    val call_id: String,
    val caller_number: String,
    val called_number: String,
    val timestamp: String,
    val action: String?,
    val message: String?,
    val status: String
)
```

### 4. Update API Interface

Add to `AIServiceApi.kt`:

```kotlin
interface AIServiceApi {
    // Existing endpoints...
    
    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<UserResponse>
    
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<UserResponse>
    
    @GET("user/profile")
    suspend fun getProfile(): Response<UserResponse>
    
    @GET("user/calls")
    suspend fun getCallHistory(@Query("limit") limit: Int = 50): Response<CallHistoryResponse>
}
```

### 5. Create Secure Storage Manager

Create `SecurePreferences.kt`:

```kotlin
package com.aiservice.client

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

object SecurePreferences {
    private const val PREFS_NAME = "secure_ai_service_prefs"
    private const val KEY_TOKEN = "jwt_token"
    private const val KEY_API_KEY = "api_key"
    private const val KEY_USERNAME = "username"
    private const val KEY_USER_ID = "user_id"
    
    private fun getPrefs(context: Context): SharedPreferences {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        
        return EncryptedSharedPreferences.create(
            context,
            PREFS_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }
    
    fun saveUser(context: Context, user: UserResponse) {
        getPrefs(context).edit().apply {
            putString(KEY_TOKEN, user.token)
            putString(KEY_API_KEY, user.api_key)
            putString(KEY_USERNAME, user.username)
            putInt(KEY_USER_ID, user.id)
            apply()
        }
    }
    
    fun getToken(context: Context): String? {
        return getPrefs(context).getString(KEY_TOKEN, null)
    }
    
    fun getApiKey(context: Context): String? {
        return getPrefs(context).getString(KEY_API_KEY, null)
    }
    
    fun getUsername(context: Context): String? {
        return getPrefs(context).getString(KEY_USERNAME, null)
    }
    
    fun isLoggedIn(context: Context): Boolean {
        return getToken(context) != null
    }
    
    fun logout(context: Context) {
        getPrefs(context).edit().clear().apply()
    }
}
```

### 6. Update ApiClient

Modify `ApiClient.kt` to include authentication:

```kotlin
object ApiClient {
    private var retrofit: Retrofit? = null
    private var currentBaseUrl: String? = null
    private var authToken: String? = null
    
    fun setAuthToken(token: String?) {
        authToken = token
        // Force recreation of retrofit instance
        retrofit = null
    }
    
    fun getClient(baseUrl: String): Retrofit {
        if (retrofit == null || currentBaseUrl != baseUrl) {
            currentBaseUrl = baseUrl
            
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            
            val authInterceptor = Interceptor { chain ->
                val request = authToken?.let {
                    chain.request().newBuilder()
                        .addHeader("Authorization", "Bearer $it")
                        .build()
                } ?: chain.request()
                chain.proceed(request)
            }
            
            val client = OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .addInterceptor(authInterceptor)
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()
            
            retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        }
        
        return retrofit!!
    }
    
    fun getApiService(baseUrl: String): AIServiceApi {
        return getClient(baseUrl).create(AIServiceApi::class.java)
    }
}
```

### 7. Create Login Activity

Create `LoginActivity.kt`:

```kotlin
package com.aiservice.client

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.aiservice.client.databinding.ActivityLoginBinding
import com.google.android.material.snackbar.Snackbar
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class LoginActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityLoginBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Check if already logged in
        if (SecurePreferences.isLoggedIn(this)) {
            goToMainActivity()
            return
        }
        
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupListeners()
    }
    
    private fun setupListeners() {
        binding.loginButton.setOnClickListener {
            login()
        }
        
        binding.registerLink.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }
    }
    
    private fun login() {
        val username = binding.usernameInput.text.toString().trim()
        val password = binding.passwordInput.text.toString()
        
        if (username.isEmpty() || password.isEmpty()) {
            showError("Please enter username and password")
            return
        }
        
        binding.loginButton.isEnabled = false
        binding.progressBar.visibility = View.VISIBLE
        
        lifecycleScope.launch {
            try {
                val serverUrl = binding.serverUrlInput.text.toString().trim()
                val api = ApiClient.getApiService(
                    if (serverUrl.endsWith("/")) serverUrl else "$serverUrl/"
                )
                
                val response = withContext(Dispatchers.IO) {
                    api.login(LoginRequest(username, password))
                }
                
                if (response.isSuccessful && response.body() != null) {
                    val user = response.body()!!
                    
                    // Save user data
                    SecurePreferences.saveUser(this@LoginActivity, user)
                    
                    // Set auth token for API client
                    ApiClient.setAuthToken(user.token)
                    
                    // Save server URL
                    getSharedPreferences("ai_service_prefs", MODE_PRIVATE).edit()
                        .putString("server_url", serverUrl)
                        .apply()
                    
                    showSuccess("Login successful!")
                    goToMainActivity()
                } else {
                    showError("Login failed: ${response.code()}")
                }
            } catch (e: Exception) {
                showError("Login error: ${e.message}")
            } finally {
                binding.loginButton.isEnabled = true
                binding.progressBar.visibility = View.GONE
            }
        }
    }
    
    private fun goToMainActivity() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
    
    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
    }
    
    private fun showSuccess(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_SHORT).show()
    }
}
```

### 8. Update MainActivity

Add to `MainActivity.kt`:

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    
    // Check authentication
    if (!SecurePreferences.isLoggedIn(this)) {
        startActivity(Intent(this, LoginActivity::class.java))
        finish()
        return
    }
    
    // Set auth token
    SecurePreferences.getToken(this)?.let {
        ApiClient.setAuthToken(it)
    }
    
    binding = ActivityMainBinding.inflate(layoutInflater)
    setContentView(binding.root)
    
    // Show username
    binding.usernameText.text = "Logged in as: ${SecurePreferences.getUsername(this)}"
    
    setupListeners()
    loadPreferences()
    updateMonitoringUI()
}

// Add logout button handler
private fun logout() {
    SecurePreferences.logout(this)
    ApiClient.setAuthToken(null)
    startActivity(Intent(this, LoginActivity::class.java))
    finish()
}
```

### 9. Update AndroidManifest.xml

Add the new activities:

```xml
<activity
    android:name=".LoginActivity"
    android:exported="true"
    android:theme="@style/Theme.AIServiceClient">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>

<activity
    android:name=".RegisterActivity"
    android:exported="false"
    android:theme="@style/Theme.AIServiceClient" />

<activity
    android:name=".MainActivity"
    android:exported="false"
    android:theme="@style/Theme.AIServiceClient" />
```

## Implementation Priority

### Phase 1: Core Authentication (Required)
1. ✅ Add dependencies
2. ✅ Create SecurePreferences
3. ✅ Update ApiClient with auth
4. ✅ Update Models
5. ✅ Update AIServiceApi

### Phase 2: UI (Required)
1. ✅ Create LoginActivity
2. ✅ Create RegisterActivity  
3. ✅ Update MainActivity
4. ✅ Update AndroidManifest

### Phase 3: Enhanced Features (Optional)
1. ⬜ Remember me functionality
2. ⬜ Forgot password
3. ⬜ Profile management
4. ⬜ Settings screen
5. ⬜ Better error handling
6. ⬜ Offline mode

## Testing Checklist

- [ ] Registration with strong password works
- [ ] Registration with weak password shows error
- [ ] Login with correct credentials works
- [ ] Login with incorrect credentials fails
- [ ] Token is stored securely
- [ ] Token is sent with API requests
- [ ] Call history shows user-specific calls
- [ ] Logout clears credentials
- [ ] App requires login after logout
- [ ] Multiple users can use different accounts

## Building the APK

After implementing all changes:

```bash
cd android-app
./gradlew assembleDebug    # For testing
./gradlew assembleRelease  # For production
```

## Notes

- All passwords must meet security requirements (12+ characters, no weak patterns)
- JWT tokens expire after 24 hours (configurable on server)
- API keys don't expire but can be regenerated
- Use encrypted SharedPreferences for all credentials
- Test on real device with real server before release
