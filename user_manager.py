"""User management for multi-user support."""
import aiosqlite
import bcrypt
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET = None  # Will be loaded from env or generated
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def get_jwt_secret() -> str:
    """Get or generate JWT secret."""
    global JWT_SECRET
    if JWT_SECRET is None:
        # Try to load from environment
        import os
        JWT_SECRET = os.getenv("JWT_SECRET")
        if not JWT_SECRET:
            # Generate a secure random secret
            JWT_SECRET = secrets.token_hex(32)
            logger.warning(
                "No JWT_SECRET found in environment. Generated temporary secret. "
                "Set JWT_SECRET in .env for production use."
            )
    return JWT_SECRET


class UserManager:
    """Manage users and authentication."""
    
    def __init__(self, db_path: str = "./users.db"):
        """
        Initialize user manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """Initialize the database."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        
        # Create tables
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS call_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                call_id TEXT NOT NULL,
                caller_number TEXT,
                called_number TEXT,
                timestamp TEXT NOT NULL,
                action TEXT,
                message TEXT,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        await self.db.commit()
        logger.info(f"User database initialized at {self.db_path}")
    
    async def close(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def generate_api_key(self) -> str:
        """Generate a secure API key."""
        return f"aisk_{secrets.token_urlsafe(32)}"
    
    def create_jwt_token(self, user_id: int, username: str) -> str:
        """Create a JWT token for a user."""
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new user.
        
        Returns:
            User data dict or None if creation failed
        """
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        try:
            password_hash = self.hash_password(password)
            api_key = self.generate_api_key()
            created_at = datetime.now(timezone.utc).isoformat()
            
            cursor = await self.db.execute(
                """
                INSERT INTO users (username, email, password_hash, api_key, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, api_key, created_at)
            )
            await self.db.commit()
            
            user_id = cursor.lastrowid
            logger.info(f"Created user: {username} (ID: {user_id})")
            
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "api_key": api_key,
                "created_at": created_at
            }
        except aiosqlite.IntegrityError as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.
        
        Returns:
            User data with JWT token or None if authentication failed
        """
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cursor = await self.db.execute(
            """
            SELECT id, username, email, password_hash, api_key, is_active
            FROM users
            WHERE username = ?
            """,
            (username,)
        )
        row = await cursor.fetchone()
        
        if not row:
            logger.warning(f"Authentication failed: user not found: {username}")
            return None
        
        user_dict = dict(row)
        
        if not user_dict["is_active"]:
            logger.warning(f"Authentication failed: user inactive: {username}")
            return None
        
        if not self.verify_password(password, user_dict["password_hash"]):
            logger.warning(f"Authentication failed: invalid password: {username}")
            return None
        
        # Update last login
        await self.db.execute(
            """
            UPDATE users
            SET last_login = ?
            WHERE id = ?
            """,
            (datetime.now(timezone.utc).isoformat(), user_dict["id"])
        )
        await self.db.commit()
        
        # Create JWT token
        token = self.create_jwt_token(user_dict["id"], user_dict["username"])
        
        logger.info(f"User authenticated: {username}")
        
        return {
            "id": user_dict["id"],
            "username": user_dict["username"],
            "email": user_dict["email"],
            "api_key": user_dict["api_key"],
            "token": token
        }
    
    async def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify an API key and return user data.
        
        Returns:
            User data or None if API key is invalid
        """
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cursor = await self.db.execute(
            """
            SELECT id, username, email, api_key
            FROM users
            WHERE api_key = ? AND is_active = 1
            """,
            (api_key,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return dict(row)
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cursor = await self.db.execute(
            """
            SELECT id, username, email, api_key, created_at, last_login
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return dict(row)
    
    async def add_call_history(
        self,
        user_id: int,
        call_id: str,
        caller_number: str,
        called_number: str,
        action: Optional[str] = None,
        message: Optional[str] = None,
        status: str = "completed"
    ) -> int:
        """
        Add a call to user's history.
        
        Returns:
            Call history record ID
        """
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        cursor = await self.db.execute(
            """
            INSERT INTO call_history
            (user_id, call_id, caller_number, called_number, timestamp, action, message, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, call_id, caller_number, called_number, timestamp, action, message, status)
        )
        await self.db.commit()
        
        return cursor.lastrowid
    
    async def get_user_call_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get call history for a user."""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cursor = await self.db.execute(
            """
            SELECT id, call_id, caller_number, called_number, timestamp, action, message, status
            FROM call_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, limit)
        )
        rows = await cursor.fetchall()
        
        return [dict(row) for row in rows]
