from typing import Optional
from pydantic import BaseModel

class SessionData(BaseModel):
    state: str = "INIT"
    symptoms: Optional[str] = None
    speciality: Optional[str] = None
    doctor: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    patient_name: Optional[str] = None
    phone: Optional[str] = None
    