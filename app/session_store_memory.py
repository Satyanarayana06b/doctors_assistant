import time
from app.session_model import SessionData

SESSION_TTL = 1800  # 30 minutes


class InMemorySessionStore:
    def __init__(self):
        self._sessions = {}
    
    def load_session(self, session_id: str) -> dict:
        """Load session data from memory"""
        record = self._sessions.get(session_id)
        if not record:
            print("No session found, initializing new session.")
            return SessionData(state="INIT").dict()
        
        # Check if session expired
        if time.time() - record["timestamp"] > SESSION_TTL:
            self._sessions.pop(session_id)
            return SessionData(state="INIT").dict()
        
        return record["data"]
    
    def save_session(self, session_id: str, data: dict):
        """Save session data to memory"""
        self._sessions[session_id] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def clear_session(self, session_id: str):
        """Delete session from memory"""
        self._sessions.pop(session_id, None)
    
    def get_all_sessions(self):
        """Get all session IDs (for debugging)"""
        return list(self._sessions.keys())
    
    def clear_all_sessions(self):
        """Clear all sessions (for testing)"""
        self._sessions.clear()
