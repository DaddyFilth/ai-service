package com.aiservice.client

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupListeners()
    }

    private fun setupListeners() {
        binding.testConnectionButton.setOnClickListener {
            testConnection()
        }

        binding.simulateCallButton.setOnClickListener {
            simulateCall()
        }
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
