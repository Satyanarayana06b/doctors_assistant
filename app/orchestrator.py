from state import ConversationState
from session_store import load_session, save_session, clear_session
from llm_client import call_llm
from prompts import SYSTEM_PROMPT

class ConversationOrchestrator:

    def handle(self, session_id: str, user_input: str) -> str:

        session = load_session(session_id)
        state = session['state']
        print(f"Current State in orchestrator: {state}")
        if state == ConversationState.INIT.value:
            return self.handle_init(session_id, session)
        
        if state == ConversationState.COLLECTING_SYMPTOMS.value:
            return self.handle_collecting_symptoms(session_id, session, user_input)
        
        if state == ConversationState.SELECTING_DOCTOR.value:
            return self.handle_selecting_doctor(session_id, session, user_input)
        
        if state == ConversationState.CHECKING_AVAILABILITY.value:
            return self.handle_availability(session_id, session, user_input)
        
        if state == ConversationState.COLLECTING_PATIENT_DETAILS.value:
            return self.handle_collecting_patient_details(session_id, session, user_input)
        
        if state == ConversationState.BOOKED.value:
            return self.handle_booking_complete(session_id, session, user_input)
        
        session['state'] = ConversationState.INIT.value
        save_session(session_id, session)
        return "Let’s start over. Please describe your health issue."
    
    def handle_init(self, session_id: str, session: dict) -> str:
        session['state'] = ConversationState.COLLECTING_SYMPTOMS.value
        save_session(session_id, session)
        return "Hello! Please describe your health issue?."
    
    def handle_collecting_symptoms(self, session_id: str, session: dict, user_input: str) -> str:
        session['symptoms'] = user_input
        # session['speciality'] = "Orthopedics"  # Placeholder for speciality inference logic
        messages = [
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content": user_input}
            ]
        response = call_llm(messages)
        speciality =  response.choices[0].message.content.strip()
        session['speciality'] = speciality
        session['state'] = ConversationState.SELECTING_DOCTOR.value
        save_session(session_id, session)
        return "Thank you. Which doctor would you like to meet? (Dr X /Dr Y)"
    
    def handle_selecting_doctor(self, session_id: str, session: dict, user_input: str) -> str:
        session['doctor'] = user_input
        session['state'] = ConversationState.CHECKING_AVAILABILITY.value
        save_session(session_id, session)
        return f"{user_input} is available tomorrow at 11 AM. Is that fine?"
    
    def handle_availability(self, session_id: str, session: dict, user_input: str) -> str:
        if user_input.lower() in ['yes', 'y', 'ok', 'fine', 'sure']:
            session['state'] = ConversationState.COLLECTING_PATIENT_DETAILS.value
            save_session(session_id, session)
            return "Great! May I have your name and contact number?"
        else:
            return "Let me check other available slots. (This feature is coming soon. Please say 'yes' to proceed.)"
    
    

    
    def handle_collecting_patient_details(self, session_id: str, session: dict, user_input: str) -> str:
        # Parse patient details (simple implementation - could be improved with regex)
        parts = user_input.split()
        if len(parts) >= 2:
            # Assume last part is phone, rest is name
            session['phone'] = parts[-1]
            session['patient_name'] = ' '.join(parts[:-1])
        else:
            session['patient_name'] = user_input
        
        # Get booking details for confirmation message
        doctor = session.get('doctor', 'the doctor')
        speciality = session.get('speciality', '')
        
        # Clear the current session completely
        clear_session(session_id)
        
        return f"Perfect! Your appointment with {doctor} ({speciality}) is confirmed for tomorrow at 11 AM. You'll receive a confirmation shortly. Thank you for choosing Super Clinic!\n\nYour session has been closed. Start a new conversation to book another appointment."
    
    
    
    
    