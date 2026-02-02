package com.aiservice.client

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

/**
 * Retrofit API interface for AI Service
 */
interface AIServiceApi {
    
    @GET("/")
    suspend fun getRoot(): Response<RootResponse>
    
    @GET("/health")
    suspend fun getHealth(): Response<HealthResponse>
    
    @POST("/call/incoming")
    suspend fun simulateCall(@Body request: CallRequest): Response<CallResponse>
    
    @GET("/call/{call_id}/status")
    suspend fun getCallStatus(@Path("call_id") callId: String): Response<Any>
}
