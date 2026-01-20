import time
from app.session_model import SessionData

_sessions = {}

SESSION_TTL = 1800 #30 minutes

def load_session(session_id: str) -> dict:
    record = _sessions.get(session_id)
    if not record:
        print("No session found, initializing new session.")
        return SessionData(state="INIT").dict()
    if time.time() - record["timestamp"] > SESSION_TTL:
        _sessions.pop(session_id)
        return SessionData().dict()
    return record["data"]

def save_session(session_id: str, data: dict):
    _sessions[session_id] = {
        "data": data,
        "timestamp": time.time()
    }

def clear_session(session_id: str):
    _sessions.pop(session_id, None)

