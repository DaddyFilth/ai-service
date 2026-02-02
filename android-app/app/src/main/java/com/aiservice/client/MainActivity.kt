package com.aiservice.client

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.aiservice.client.databinding.ActivityMainBinding
import com.google.android.material.snackbar.Snackbar
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private var isConnected = false
    private var monitoringEnabled = false

    companion object {
        private const val PERMISSIONS_REQUEST_CODE = 123
        private val REQUIRED_PERMISSIONS = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            arrayOf(
                Manifest.permission.READ_PHONE_STATE,
                Manifest.permission.READ_CALL_LOG,
                Manifest.permission.ANSWER_PHONE_CALLS
            )
        } else {
            arrayOf(
                Manifest.permission.READ_PHONE_STATE,
                Manifest.permission.READ_CALL_LOG
            )
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupListeners()
        loadPreferences()
        updateMonitoringUI()
    }

    private fun loadPreferences() {
        val prefs = getSharedPreferences("ai_service_prefs", Context.MODE_PRIVATE)
        val savedUrl = prefs.getString("server_url", "")
        if (!savedUrl.isNullOrEmpty()) {
            binding.serverUrlInput.setText(savedUrl)
        }
        monitoringEnabled = prefs.getBoolean("monitoring_enabled", false)
    }

    private fun savePreferences() {
        val prefs = getSharedPreferences("ai_service_prefs", Context.MODE_PRIVATE)
        prefs.edit().apply {
            putString("server_url", binding.serverUrlInput.text.toString().trim())
            putBoolean("monitoring_enabled", monitoringEnabled)
            apply()
        }
    }

    private fun setupListeners() {
        binding.testConnectionButton.setOnClickListener {
            testConnection()
        }

        binding.simulateCallButton.setOnClickListener {
            simulateCall()
        }
        
        binding.toggleMonitoringButton.setOnClickListener {
            toggleCallMonitoring()
        }
        
        binding.viewHistoryButton.setOnClickListener {
            viewCallHistory()
        }
    }

    private fun toggleCallMonitoring() {
        if (monitoringEnabled) {
            // Disable monitoring
            monitoringEnabled = false
            savePreferences()
            updateMonitoringUI()
            showSuccess("Call monitoring disabled")
        } else {
            // Enable monitoring - check permissions first
            if (hasRequiredPermissions()) {
                enableMonitoring()
            } else {
                requestRequiredPermissions()
            }
        }
    }

    private fun hasRequiredPermissions(): Boolean {
        return REQUIRED_PERMISSIONS.all { permission ->
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
        }
    }

    private fun requestRequiredPermissions() {
        ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, PERMISSIONS_REQUEST_CODE)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == PERMISSIONS_REQUEST_CODE) {
            if (grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                enableMonitoring()
            } else {
                showError("Permissions required to monitor calls")
            }
        }
    }

    private fun enableMonitoring() {
        val serverUrl = binding.serverUrlInput.text.toString().trim()
        
        if (serverUrl.isEmpty()) {
            showError("Please enter and test server URL first")
            return
        }
        
        if (!isConnected) {
            showError("Please test connection to server first")
            return
        }
        
        monitoringEnabled = true
        savePreferences()
        updateMonitoringUI()
        showSuccess("Call monitoring enabled - incoming calls will be forwarded to AI service")
    }

    private fun updateMonitoringUI() {
        if (monitoringEnabled) {
            binding.toggleMonitoringButton.text = "Disable Call Monitoring"
            binding.monitoringStatusText.text = "Status: ACTIVE"
            binding.monitoringStatusText.setTextColor(getColor(R.color.green))
        } else {
            binding.toggleMonitoringButton.text = "Enable Call Monitoring"
            binding.monitoringStatusText.text = "Status: INACTIVE"
            binding.monitoringStatusText.setTextColor(getColor(R.color.red))
        }
    }

    private fun viewCallHistory() {
        val prefs = getSharedPreferences("ai_service_prefs", Context.MODE_PRIVATE)
        val history = prefs.getStringSet("call_history", setOf())?.sortedDescending() ?: emptyList()
        
        if (history.isEmpty()) {
            binding.responseText.text = "No call history yet"
            return
        }
        
        val historyText = StringBuilder("Call History:\n\n")
        history.take(20).forEach { entry ->
            val parts = entry.split("|")
            if (parts.size == 4) {
                val (timestamp, number, action, message) = parts
                historyText.append("Time: $timestamp\n")
                historyText.append("From: $number\n")
                historyText.append("AI Action: $action\n")
                historyText.append("Message: $message\n")
                historyText.append("─".repeat(40))
                historyText.append("\n\n")
            }
        }
        
        binding.responseText.text = historyText.toString()
    }

    private fun testConnection() {
        val serverUrl = binding.serverUrlInput.text.toString().trim()
        
        if (serverUrl.isEmpty()) {
            showError("Please enter a server URL")
            return
        }

        // Ensure URL format is correct
        val formattedUrl = if (!serverUrl.endsWith("/")) "$serverUrl/" else serverUrl

        binding.testConnectionButton.isEnabled = false
        binding.connectionStatusText.text = getString(R.string.testing)
        binding.connectionStatusText.setTextColor(getColor(R.color.gray))
        binding.responseText.text = ""

        lifecycleScope.launch {
            try {
                val api = ApiClient.getApiService(formattedUrl)
                
                val response = withContext(Dispatchers.IO) {
                    api.getHealth()
                }

                if (response.isSuccessful) {
                    val healthResponse = response.body()
                    isConnected = true
                    binding.connectionStatusText.text = getString(R.string.connected)
                    binding.connectionStatusText.setTextColor(getColor(R.color.green))
                    
                    val responseJson = "Health Check Success:\n" +
                            "Status: ${healthResponse?.status}\n" +
                            "Components: ${healthResponse?.components}"
                    binding.responseText.text = responseJson
                    
                    showSuccess("Connected to AI Service successfully!")
                } else {
                    handleConnectionError("Server returned error: ${response.code()}")
                }
            } catch (e: Exception) {
                handleConnectionError("Connection failed: ${e.message}")
            } finally {
                binding.testConnectionButton.isEnabled = true
            }
        }
    }

    private fun simulateCall() {
        val serverUrl = binding.serverUrlInput.text.toString().trim()
        
        if (serverUrl.isEmpty()) {
            showError("Please enter a server URL")
            return
        }

        val callId = binding.callIdInput.text.toString().trim()
        val callerNumber = binding.callerNumberInput.text.toString().trim()
        val calledNumber = binding.calledNumberInput.text.toString().trim()

        if (callId.isEmpty() || callerNumber.isEmpty() || calledNumber.isEmpty()) {
            showError("Please fill in all call fields")
            return
        }

        // Ensure URL format is correct
        val formattedUrl = if (!serverUrl.endsWith("/")) "$serverUrl/" else serverUrl

        binding.simulateCallButton.isEnabled = false
        binding.responseText.text = "Sending call request..."

        lifecycleScope.launch {
            try {
                val api = ApiClient.getApiService(formattedUrl)
                
                // Create timestamp in ISO format
                val timestamp = SimpleDateFormat(
                    "yyyy-MM-dd'T'HH:mm:ss'Z'",
                    Locale.getDefault()
                ).apply {
                    timeZone = TimeZone.getTimeZone("UTC")
                }.format(Date())
                
                val callRequest = CallRequest(
                    callId = callId,
                    callerNumber = callerNumber,
                    calledNumber = calledNumber,
                    timestamp = timestamp,
                    channel = "Android-App"
                )

                val response = withContext(Dispatchers.IO) {
                    api.simulateCall(callRequest)
                }

                if (response.isSuccessful) {
                    val callResponse = response.body()
                    
                    val responseJson = "Call Simulated Successfully:\n\n" +
                            "Call ID: ${callResponse?.callId}\n" +
                            "Status: ${callResponse?.status}\n" +
                            "Action: ${callResponse?.action ?: "N/A"}\n" +
                            "Message: ${callResponse?.message ?: "N/A"}"
                    
                    binding.responseText.text = responseJson
                    binding.responseText.visibility = View.VISIBLE
                    
                    showSuccess("Call simulated successfully!")
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Unknown error"
                    binding.responseText.text = "Error: ${response.code()}\n$errorBody"
                    showError("Call simulation failed: ${response.code()}")
                }
            } catch (e: Exception) {
                binding.responseText.text = "Exception: ${e.message}\n${e.stackTraceToString()}"
                showError("Call simulation failed: ${e.message}")
            } finally {
                binding.simulateCallButton.isEnabled = true
            }
        }
    }

    private fun handleConnectionError(message: String) {
        isConnected = false
        binding.connectionStatusText.text = getString(R.string.not_connected)
        binding.connectionStatusText.setTextColor(getColor(R.color.red))
        binding.responseText.text = message
        showError(message)
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }

    private fun showSuccess(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_SHORT).show()
    }
}
