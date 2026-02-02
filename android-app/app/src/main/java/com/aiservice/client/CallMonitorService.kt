package com.aiservice.client

import android.app.*
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*
import java.text.SimpleDateFormat
import java.util.*

/**
 * Foreground service to monitor calls and forward them to the AI server
 */
class CallMonitorService : Service() {
    
    companion object {
        const val TAG = "CallMonitorService"
        const val CHANNEL_ID = "call_monitor_channel"
        const val NOTIFICATION_ID = 1
        
        const val ACTION_INCOMING_CALL = "com.aiservice.client.INCOMING_CALL"
        const val ACTION_STOP_MONITORING = "com.aiservice.client.STOP_MONITORING"
        
        const val EXTRA_PHONE_NUMBER = "phone_number"
        const val EXTRA_SERVER_URL = "server_url"
    }
    
    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Service created")
        createNotificationChannel()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Service started with action: ${intent?.action}")
        
        when (intent?.action) {
            ACTION_INCOMING_CALL -> {
                val phoneNumber = intent.getStringExtra(EXTRA_PHONE_NUMBER)
                val serverUrl = intent.getStringExtra(EXTRA_SERVER_URL)
                
                if (phoneNumber != null && serverUrl != null) {
                    startForeground(NOTIFICATION_ID, createNotification("Processing call from $phoneNumber"))
                    handleIncomingCall(phoneNumber, serverUrl)
                } else {
                    Log.e(TAG, "Missing phone number or server URL")
                    stopSelf()
                }
            }
            ACTION_STOP_MONITORING -> {
                stopSelf()
            }
            else -> {
                // Start with default notification if no specific action
                startForeground(NOTIFICATION_ID, createNotification("Call monitoring active"))
            }
        }
        
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
    
    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
        Log.d(TAG, "Service destroyed")
    }
    
    private fun handleIncomingCall(phoneNumber: String, serverUrl: String) {
        serviceScope.launch {
            try {
                Log.d(TAG, "Forwarding call from $phoneNumber to server: $serverUrl")
                
                // Update notification
                updateNotification("Processing call from $phoneNumber...")
                
                // Create call request
                val callId = "android_${System.currentTimeMillis()}"
                val timestamp = SimpleDateFormat(
                    "yyyy-MM-dd'T'HH:mm:ss'Z'",
                    Locale.getDefault()
                ).apply {
                    timeZone = TimeZone.getTimeZone("UTC")
                }.format(Date())
                
                val callRequest = CallRequest(
                    callId = callId,
                    callerNumber = phoneNumber,
                    calledNumber = "local", // The local device number
                    timestamp = timestamp,
                    channel = "Android-Device"
                )
                
                // Send to AI service
                val api = ApiClient.getApiService(serverUrl)
                val response = withContext(Dispatchers.IO) {
                    api.simulateCall(callRequest)
                }
                
                if (response.isSuccessful) {
                    val callResponse = response.body()
                    val action = callResponse?.action ?: "unknown"
                    val message = callResponse?.message ?: "No message"
                    
                    Log.d(TAG, "AI Decision - Action: $action, Message: $message")
                    
                    // Save call to history
                    saveCallToHistory(phoneNumber, action, message)
                    
                    // Update notification with AI decision
                    updateNotification("AI Decision: $action - $message")
                    
                    // Keep notification visible for 10 seconds
                    delay(10000)
                } else {
                    Log.e(TAG, "Server error: ${response.code()}")
                    updateNotification("Server error: ${response.code()}")
                    delay(10000)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error processing call", e)
                updateNotification("Error: ${e.message}")
                delay(10000)
            } finally {
                stopSelf()
            }
        }
    }
    
    private fun saveCallToHistory(phoneNumber: String, action: String, message: String) {
        try {
            val prefs = getSharedPreferences("ai_service_prefs", Context.MODE_PRIVATE)
            val history = prefs.getStringSet("call_history", mutableSetOf())?.toMutableSet() ?: mutableSetOf()
            
            val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date())
            val entry = "$timestamp|$phoneNumber|$action|$message"
            
            history.add(entry)
            
            // Keep only last 50 entries
            if (history.size > 50) {
                val sortedHistory = history.sorted().toMutableSet()
                while (sortedHistory.size > 50) {
                    sortedHistory.remove(sortedHistory.first())
                }
                prefs.edit().putStringSet("call_history", sortedHistory).apply()
            } else {
                prefs.edit().putStringSet("call_history", history).apply()
            }
            
            Log.d(TAG, "Call saved to history")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to save call to history", e)
        }
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Call Monitoring",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Notifications for incoming call monitoring"
            }
            
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(contentText: String): Notification {
        val notificationIntent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, notificationIntent,
            PendingIntent.FLAG_IMMUTABLE
        )
        
        val stopIntent = Intent(this, CallMonitorService::class.java).apply {
            action = ACTION_STOP_MONITORING
        }
        val stopPendingIntent = PendingIntent.getService(
            this, 0, stopIntent,
            PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("AI Call Service")
            .setContentText(contentText)
            .setSmallIcon(android.R.drawable.ic_menu_call)
            .setContentIntent(pendingIntent)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Stop", stopPendingIntent)
            .build()
    }
    
    private fun updateNotification(contentText: String) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID, createNotification(contentText))
    }
}
