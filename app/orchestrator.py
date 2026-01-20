from app.state import ConversationState
from app.session_store import load_session, save_session, clear_session
from app.llm_client import call_llm
from app.prompts import SYSTEM_PROMPT, SPECIALITY_INFERENCE_PROMPT
from db.schedule_repo import is_slot_available, get_available_slots
from db.booking_repo import book_appointment
from db.doctor_repo import get_doctors_by_speciality

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
        # Use specialized prompt to infer medical specialty
        messages = [
            {"role":"system", "content":SPECIALITY_INFERENCE_PROMPT},
            {"role":"user", "content": user_input}
            ]
        response = call_llm(messages)
        speciality = response.choices[0].message.content.strip()
        
        # Validate specialty - should be reasonable length and contain only letters/spaces
        if not speciality or len(speciality) > 50 or not all(c.isalpha() or c.isspace() for c in speciality):
            print(f" Invalid LLM output: '{speciality}', defaulting to General Medicine")
            speciality = "General Medicine"
        
        print(f"======Inferred speciality: {speciality}")
        session['speciality'] = speciality
        
        # Get doctors by specialty from database
        doctors = get_doctors_by_speciality(speciality)
        if not doctors:
            return f"Sorry, we don't have any {speciality} specialists available at the moment. Please describe your symptoms differently."
        
        # Format doctor names for display
        doctor_names = " / ".join([doc[1] for doc in doctors])
        session['state'] = ConversationState.SELECTING_DOCTOR.value
        save_session(session_id, session)
        return f"Thank you. Which doctor would you like to meet? ({doctor_names})"
    
    def handle_selecting_doctor(self, session_id: str, session: dict, user_input: str) -> str:
        session['doctor_name'] = user_input
        
        # Get doctor_id from database
        doctors = get_doctors_by_speciality(session.get('speciality', ''))
        print(f"Doctors fetched for speciality {session.get('speciality', '')}: {doctors}") 
        doctor_id = None
        for doc in doctors:
            if doc[1] == user_input:  # doc[1] is the name
                doctor_id = doc[0]  # doc[0] is the id
                break
        
        if not doctor_id:
            return f"Sorry, I couldn't find {user_input}. Please select a valid doctor."
        
        session['doctor_id'] = doctor_id
        
        # Get available slots for this doctor
        available_slots = get_available_slots(doctor_id)
        
        if not available_slots:
            return f"Sorry, {user_input} has no available slots at the moment."
        
        # Use the first available slot
        first_slot = available_slots[0]
        session['date'] = str(first_slot[0])  # schedule_date
        session['time'] = str(first_slot[1])  # start_time
        
        session['state'] = ConversationState.CHECKING_AVAILABILITY.value
        save_session(session_id, session)
        
        return f"{user_input} is available on {first_slot[0]} at {first_slot[1]}. Is that fine?"
    
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
        doctor_name = session.get('doctor_name', 'the doctor')
        speciality = session.get('speciality', '')
        doctor_id = session.get('doctor_id')
        date = session.get('date')
        time = session.get('time')
        
        # Book the appointment in database
        try:
            book_appointment(
                doctor_id=doctor_id,
                patient_name=session['patient_name'],
                phone=session['phone'],
                date=date,
                time=time
            )
        except Exception as e:
            return f"Sorry, there was an error booking your appointment: {str(e)}"
        
        # Clear the current session completely
        clear_session(session_id)
        
        return f"Perfect! Your appointment with {doctor_name} ({speciality}) is confirmed for {date} at {time}. You'll receive a confirmation shortly. Thank you for choosing Super Clinic!\n\nYour session has been closed. Start a new conversation to book another appointment."
    
    
    
    
    