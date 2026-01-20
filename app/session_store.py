import os
from dotenv import load_dotenv

load_dotenv()

# Determine which session store to use
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"

# Initialize the appropriate session store
_store = None

if USE_REDIS:
    try:
        from app.session_store_redis import RedisSessionStore
        _store = RedisSessionStore()
        print("Using Redis session store")
    except Exception as e:
        print(f"Failed to initialize Redis: {e}")
        print("Falling back to in-memory session store")
        from app.session_store_memory import InMemorySessionStore
        _store = InMemorySessionStore()
else:
    from app.session_store_memory import InMemorySessionStore
    _store = InMemorySessionStore()
    print("Using in-memory session store")


# Public API
def load_session(session_id: str) -> dict:
    """Load session data"""
    # return _store.load_session(session_id)
    try:
        session = _store.load_session(session_id)
    except Exception: 
        session = {"state": "INIT"}
    return session



def save_session(session_id: str, data: dict):
    """Save session data"""
    _store.save_session(session_id, data)


def clear_session(session_id: str):
    """Clear a specific session"""
    _store.clear_session(session_id)


def get_all_sessions():
    """Get all session IDs (for debugging)"""
    return _store.get_all_sessions()


def clear_all_sessions():
    """Clear all sessions (for testing)"""
    _store.clear_all_sessions()

