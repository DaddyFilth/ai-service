"""FastAPI web server for AI call service."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging

from main import AICallService
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="AI Call Service API", version="1.0.0")

# Global service instance
service: Optional[AICallService] = None


class CallRequest(BaseModel):
    """Request model for incoming calls."""
    call_id: str
    caller_number: str
    called_number: str
    timestamp: Optional[str] = None
    channel: Optional[str] = None


class CallResponse(BaseModel):
    """Response model for call handling."""
    status: str
    call_id: str
    action: Optional[str] = None
    message: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the AI service on startup."""
    global service
    logger.info("Starting up AI Call Service API")
    service = AICallService()
    await service.start()
    logger.info("AI Call Service API is ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global service
    if service:
        await service.stop()
    logger.info("AI Call Service API shut down")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AI Call Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "sip": service.sip.connected if service else False,
            "stt": service.stt.model is not None if service else False,
            "decision_engine": True,
            "action_router": True
        }
    }


@app.post("/call/incoming", response_model=CallResponse)
async def handle_incoming_call(call_request: CallRequest):
    """
    Handle an incoming call.
    
    This endpoint would typically be called by Asterisk via HTTP/webhook.
    """
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    call_data = call_request.dict()
    logger.info(f"Received incoming call: {call_data}")
    
    try:
        result = await service.handle_call(call_data)
        return CallResponse(
            status=result.get("status", "success"),
            call_id=call_request.call_id,
            action=result.get("action"),
            message=result.get("message")
        )
    except Exception as e:
        logger.error(f"Error handling call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/call/{call_id}/status")
async def get_call_status(call_id: str):
    """Get the status of a specific call."""
    # In a real implementation, this would track call states
    return {
        "call_id": call_id,
        "status": "active",
        "message": "Call status tracking not yet implemented"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.service_host,
        port=settings.service_port,
        log_level="info"
    )
