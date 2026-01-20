import json
import os
from dotenv import load_dotenv
import redis
from app.session_model import SessionData

load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

SESSION_TTL = 1800  # 30 minutes


class RedisSessionStore:
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            print(" Connected to Redis for session storage")
        except redis.ConnectionError as e:
            print(f" Redis connection failed: {e}")
            self.client = None
            raise
    
    def is_connected(self):
        """Check if Redis is connected"""
        return self.client is not None
    
    def load_session(self, session_id: str) -> dict:
        """Load session data from Redis"""
        if not self.client:
            raise RuntimeError("Redis client is not connected")
        
        data = self.client.get(f"session:{session_id}")
        if not data:
            print("No session found, initializing new session.")
            return SessionData(state="INIT").dict()
        
        return json.loads(data)
    
    def save_session(self, session_id: str, data: dict):
        """Save session data to Redis with TTL"""
        if not self.client:
            raise RuntimeError("Redis client is not connected")
        
        self.client.setex(
            f"session:{session_id}",
            SESSION_TTL,
            json.dumps(data)
        )
    
    def clear_session(self, session_id: str):
        """Delete session from Redis"""
        if not self.client:
            raise RuntimeError("Redis client is not connected")
        
        self.client.delete(f"session:{session_id}")
    
    def get_all_sessions(self):
        """Get all session keys (for debugging)"""
        if not self.client:
            raise RuntimeError("Redis client is not connected")
        
        return self.client.keys("session:*")
    
    def clear_all_sessions(self):
        """Clear all sessions (for testing)"""
        if not self.client:
            raise RuntimeError("Redis client is not connected")
        
        keys = self.client.keys("session:*")
        if keys:
            self.client.delete(*keys)
