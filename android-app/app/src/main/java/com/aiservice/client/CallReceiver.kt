package com.aiservice.client

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.telephony.TelephonyManager
import android.util.Log
import android.widget.Toast

/**
 * BroadcastReceiver to detect incoming phone calls
 */
class CallReceiver : BroadcastReceiver() {
    
    companion object {
        private const val TAG = "CallReceiver"
    }
    
    override fun onReceive(context: Context?, intent: Intent?) {
        if (context == null || intent == null) return
        
        if (intent.action == TelephonyManager.ACTION_PHONE_STATE_CHANGED) {
            val state = intent.getStringExtra(TelephonyManager.EXTRA_STATE)
            val incomingNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER)
            
            Log.d(TAG, "Phone state changed: $state, Number: $incomingNumber")
            
            when (state) {
                TelephonyManager.EXTRA_STATE_RINGING -> {
                    // Incoming call detected
                    if (incomingNumber != null) {
                        handleIncomingCall(context, incomingNumber)
                    }
                }
                TelephonyManager.EXTRA_STATE_OFFHOOK -> {
                    // Call answered
                    Log.d(TAG, "Call answered")
                }
                TelephonyManager.EXTRA_STATE_IDLE -> {
                    // Call ended
                    Log.d(TAG, "Call ended")
                }
            }
        }
    }
    
    private fun handleIncomingCall(context: Context, phoneNumber: String) {
        Log.d(TAG, "Incoming call from: $phoneNumber")
        
        // Check if monitoring is enabled
        val prefs = context.getSharedPreferences("ai_service_prefs", Context.MODE_PRIVATE)
        val monitoringEnabled = prefs.getBoolean("monitoring_enabled", false)
        val serverUrl = prefs.getString("server_url", "")
        
        if (!monitoringEnabled || serverUrl.isNullOrEmpty()) {
            Log.d(TAG, "Monitoring disabled or server URL not set")
            return
        }
        
        // Start the call monitor service to handle this call
        val serviceIntent = Intent(context, CallMonitorService::class.java).apply {
            action = CallMonitorService.ACTION_INCOMING_CALL
            putExtra(CallMonitorService.EXTRA_PHONE_NUMBER, phoneNumber)
            putExtra(CallMonitorService.EXTRA_SERVER_URL, serverUrl)
        }
        
        try {
            context.startForegroundService(serviceIntent)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start CallMonitorService", e)
            Toast.makeText(context, "Failed to process call: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}
