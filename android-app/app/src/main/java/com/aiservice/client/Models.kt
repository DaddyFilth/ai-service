package com.aiservice.client

import com.google.gson.annotations.SerializedName

/**
 * Request model for incoming call
 */
data class CallRequest(
    @SerializedName("call_id")
    val callId: String,
    
    @SerializedName("caller_number")
    val callerNumber: String,
    
    @SerializedName("called_number")
    val calledNumber: String,
    
    @SerializedName("timestamp")
    val timestamp: String? = null,
    
    @SerializedName("channel")
    val channel: String? = null
)

/**
 * Response model for call handling
 */
data class CallResponse(
    @SerializedName("status")
    val status: String,
    
    @SerializedName("call_id")
    val callId: String,
    
    @SerializedName("action")
    val action: String? = null,
    
    @SerializedName("message")
    val message: String? = null
)

/**
 * Health check response
 */
data class HealthResponse(
    @SerializedName("status")
    val status: String,
    
    @SerializedName("components")
    val components: Map<String, Any>? = null
)

/**
 * Root endpoint response
 */
data class RootResponse(
    @SerializedName("service")
    val service: String,
    
    @SerializedName("version")
    val version: String,
    
    @SerializedName("status")
    val status: String
)
