package com.aiservice.client

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * API client for AI Service
 */
object ApiClient {
    
    private var retrofit: Retrofit? = null
    private var currentBaseUrl: String? = null
    
    /**
     * Get or create Retrofit instance
     */
    fun getClient(baseUrl: String): Retrofit {
        // Recreate if URL changed
        if (retrofit == null || currentBaseUrl != baseUrl) {
            currentBaseUrl = baseUrl
            
            // Create logging interceptor
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            
            // Create OkHttp client
            val client = OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()
            
            // Create Retrofit instance
            retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        }
        
        return retrofit!!
    }
    
    /**
     * Get API service instance
     */
    fun getApiService(baseUrl: String): AIServiceApi {
        return getClient(baseUrl).create(AIServiceApi::class.java)
    }
}
