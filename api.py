"""Aiohttp web server for AI call service with multi-user support."""
from aiohttp import web
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional
import functools
from datetime import datetime, timezone
import logging
import json

from main import AICallService
from config import settings
from user_manager import UserManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
MAX_CALL_HISTORY_LIMIT = 500  # Maximum number of call history records to return

# Global instances
service: Optional[AICallService] = None
user_manager: Optional[UserManager] = None
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


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    username: str
    email: str
    api_key: str
    token: Optional[str] = None


async def startup_event(app):
    """Initialize the AI service on startup."""
    global service, user_manager
    logger.info("Starting up AI Call Service API")

    # Initialize user manager
    user_manager = UserManager()
    await user_manager.initialize()
    logger.info("User manager initialized")

    # Initialize AI service
    service = AICallService()
    await service.start()
    logger.info("AI Call Service API is ready")


async def cleanup_event(app):
    """Cleanup on shutdown."""
    if service:
        await service.stop()
    if user_manager:
        await user_manager.close()
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
            "action_router": True,
            "user_manager": user_manager is not None
        }
    })


async def get_current_user(request) -> Optional[Dict[str, Any]]:
    """
    Extract and verify user from request headers.
    Supports both JWT tokens and API keys.
    """
    # Try JWT token first
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        payload = user_manager.verify_jwt_token(token)
        if payload:
            user = await user_manager.get_user_by_id(payload['user_id'])
            return user

    # Try API key
    api_key = request.headers.get('X-API-Key', '')
    if api_key:
        user = await user_manager.verify_api_key(api_key)
        return user

    return None


def require_auth(handler):
    """Decorator to require authentication."""
    @functools.wraps(handler)
    async def wrapper(request):
        user = await get_current_user(request)
        if not user:
            return web.json_response(
                {"detail": "Authentication required"},
                status=401
            )
        request['user'] = user
        return await handler(request)
    return wrapper


async def handle_incoming_call(request):
    """
    Handle an incoming call.

    This endpoint would typically be called by Asterisk via HTTP/webhook
    or by authenticated mobile app users.
    """
    if not service:
        return web.json_response(
            {"detail": "Service not initialized"},
            status=503
        )

    # Get user if authenticated (optional for backwards compatibility)
    user = await get_current_user(request)
    user_id = user['id'] if user else None

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
    logger.info(f"Received incoming call: {call_data} (user_id: {user_id})")

    try:
        call_status_store[call_request.call_id] = {
            "call_id": call_request.call_id,
            "user_id": user_id,
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

        # Save to user's call history if authenticated
        if user_id and user_manager:
            await user_manager.add_call_history(
                user_id=user_id,
                call_id=call_request.call_id,
                caller_number=call_request.caller_number,
                called_number=call_request.called_number,
                action=result.get("action"),
                message=result.get("message"),
                status=result.get("status", "success")
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
            "user_id": user_id,
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


async def register_user(request):
    """Register a new user."""
    if not user_manager:
        return web.json_response(
            {"detail": "User management not available"},
            status=503
        )

    try:
        data = await request.json()
        user_request = UserRegisterRequest(**data)
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

    # Validate password strength
    from config import validate_password_strength
    is_valid, error_msg = validate_password_strength(user_request.password)
    if not is_valid:
        return web.json_response(
            {"detail": f"Weak password: {error_msg}"},
            status=400
        )

    user_data = await user_manager.create_user(
        username=user_request.username,
        email=user_request.email,
        password=user_request.password
    )

    if not user_data:
        return web.json_response(
            {"detail": "Username or email already exists"},
            status=409
        )

    # Create token for immediate login
    token = user_manager.create_jwt_token(
        user_data["id"], user_data["username"])
    user_data["token"] = token

    response = UserResponse(**user_data)
    return web.json_response(response.dict())


async def login_user(request):
    """Authenticate user and return token."""
    if not user_manager:
        return web.json_response(
            {"detail": "User management not available"},
            status=503
        )

    try:
        data = await request.json()
        login_request = UserLoginRequest(**data)
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

    user_data = await user_manager.authenticate(
        username=login_request.username,
        password=login_request.password
    )

    if not user_data:
        return web.json_response(
            {"detail": "Invalid username or password"},
            status=401
        )

    response = UserResponse(**user_data)
    return web.json_response(response.dict())


@require_auth
async def get_user_profile(request):
    """Get current user's profile."""
    user = request['user']
    return web.json_response(user)


@require_auth
async def get_user_call_history(request):
    """Get call history for current user."""
    user = request['user']

    # Get limit from query params with proper validation
    try:
        limit = int(request.query.get('limit', '50'))
        # Ensure limit is positive and within bounds
        if limit < 1 or limit > MAX_CALL_HISTORY_LIMIT:
            return web.json_response(
                {
                    "detail": (
                        f"Invalid limit parameter - must be between 1 "
                        f"and {MAX_CALL_HISTORY_LIMIT}"
                    )
                },
                status=400
            )
    except ValueError:
        return web.json_response(
            {"detail": "Invalid limit parameter - must be an integer"},
            status=400
        )

    history = await user_manager.get_user_call_history(user['id'], limit)

    return web.json_response({
        "user_id": user['id'],
        "username": user['username'],
        "total_calls": len(history),
        "calls": history
    })


def create_app():
    """Create and configure the aiohttp application."""
    app = web.Application()

    # Setup routes
    app.router.add_get('/', root)
    app.router.add_get('/health', health_check)

    # Call handling routes
    app.router.add_post('/call/incoming', handle_incoming_call)
    app.router.add_get('/call/{call_id}/status', get_call_status)

    # User management routes
    app.router.add_post('/auth/register', register_user)
    app.router.add_post('/auth/login', login_user)
    app.router.add_get('/user/profile', get_user_profile)
    app.router.add_get('/user/calls', get_user_call_history)

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
