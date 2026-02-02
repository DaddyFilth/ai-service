"""Aiohttp web server for AI call service."""
from aiohttp import web
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime, timezone
import logging
import json

from main import AICallService
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instance
service: Optional[AICallService] = None
call_status_store: Dict[str, Dict[str, Any]] = {}


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


async def startup_event(app):
    """Initialize the AI service on startup."""
    global service
    logger.info("Starting up AI Call Service API")
    service = AICallService()
    await service.start()
    logger.info("AI Call Service API is ready")


async def cleanup_event(app):
    """Cleanup on shutdown."""
    global service
    if service:
        await service.stop()
    logger.info("AI Call Service API shut down")


async def root(request):
    """Root endpoint."""
    return web.json_response({
        "service": "AI Call Service",
        "version": "1.0.0",
        "status": "running"
    })


async def health_check(request):
    """Health check endpoint."""
    return web.json_response({
        "status": "healthy",
        "components": {
            "sip": service.sip.connected if service else False,
            "stt": service.stt.model is not None if service else False,
            "decision_engine": True,
            "action_router": True
        }
    })


async def handle_incoming_call(request):
    """
    Handle an incoming call.
    
    This endpoint would typically be called by Asterisk via HTTP/webhook.
    """
    if not service:
        return web.json_response(
            {"detail": "Service not initialized"},
            status=503
        )
    
    try:
        data = await request.json()
        # Validate the request using Pydantic
        call_request = CallRequest(**data)
    except json.JSONDecodeError:
        return web.json_response(
            {"detail": "Invalid JSON"},
            status=400
        )
    except ValidationError as e:
        return web.json_response(
            {"detail": str(e)},
            status=422
        )
    
    call_data = call_request.dict()
    logger.info(f"Received incoming call: {call_data}")
    
    try:
        call_status_store[call_request.call_id] = {
            "call_id": call_request.call_id,
            "status": "in_progress",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "action": None,
            "message": None,
        }
        result = await service.handle_call(call_data)
        call_status_store[call_request.call_id].update(
            {
                "status": result.get("status", "success"),
                "action": result.get("action"),
                "message": result.get("message"),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        response = CallResponse(
            status=result.get("status", "success"),
            call_id=call_request.call_id,
            action=result.get("action"),
            message=result.get("message")
        )
        return web.json_response(response.dict())
    except Exception as e:
        call_status_store[call_request.call_id] = {
            "call_id": call_request.call_id,
            "status": "error",
            "error": str(e),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.error(f"Error handling call: {e}")
        return web.json_response(
            {"detail": str(e)},
            status=500
        )


async def get_call_status(request):
    """Get the status of a specific call."""
    call_id = request.match_info['call_id']
    status = call_status_store.get(call_id)
    if not status:
        return web.json_response(
            {"detail": "Call ID not found"},
            status=404
        )
    return web.json_response(status)


def create_app():
    """Create and configure the aiohttp application."""
    app = web.Application()
    
    # Setup routes
    app.router.add_get('/', root)
    app.router.add_get('/health', health_check)
    app.router.add_post('/call/incoming', handle_incoming_call)
    app.router.add_get('/call/{call_id}/status', get_call_status)
    
    # Setup startup and cleanup
    app.on_startup.append(startup_event)
    app.on_cleanup.append(cleanup_event)
    
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(
        app,
        host=settings.service_host,
        port=settings.service_port
    )
