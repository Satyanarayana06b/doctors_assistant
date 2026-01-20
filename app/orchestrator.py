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
        
        if state == ConversationState.OFFERING_ALTERNATIVE_DOCTOR.value:
            return self.handle_alternative_doctor(session_id, session, user_input)
        
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
            # No doctors for this specialty
            clear_session(session_id)
            return f"Sorry, we don't have any {speciality} specialists available at the moment. Please try again later."
        
        # Check if any doctor has available slots
        has_available_slots = False
        for doc in doctors:
            slots = get_available_slots(doc[0])  # doc[0] is doctor_id
            if slots:
                has_available_slots = True
                break
        
        if not has_available_slots:
            # Doctors exist but no slots available
            clear_session(session_id)
            return f"Sorry, all our {speciality} specialists are fully booked at the moment. Please try again later. Thank you!"
        
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
            # Check if there are other doctors with slots
            other_doctors = [doc for doc in doctors if doc[0] != doctor_id]
            doctors_with_slots = []
            
            for doc in other_doctors:
                slots = get_available_slots(doc[0])
                if slots:
                    doctors_with_slots.append(doc)
            
            if doctors_with_slots:
                # Offer alternative doctors
                session['alternative_doctors'] = [(doc[0], doc[1]) for doc in doctors_with_slots]
                session['state'] = ConversationState.OFFERING_ALTERNATIVE_DOCTOR.value
                save_session(session_id, session)
                
                alt_names = ", ".join([doc[1] for doc in doctors_with_slots])
                return f"Sorry, {user_input} has no available slots at the moment. However, we have other doctors available: {alt_names}. Would you like to proceed with one of them? (yes/no)"
            else:
                # No alternative doctors available
                clear_session(session_id)
                return f"Sorry, {user_input} and all other {session.get('speciality', '')} specialists are fully booked. Please try again later. Thank you!"
        
        # Use the first available slot
        first_slot = available_slots[0]
        session['date'] = str(first_slot[0])  # schedule_date
        session['time'] = str(first_slot[1])  # start_time
        
        session['state'] = ConversationState.CHECKING_AVAILABILITY.value
        save_session(session_id, session)
        
        return f"{user_input} is available on {first_slot[0]} at {first_slot[1]}. Is that fine?"
    
    def handle_alternative_doctor(self, session_id: str, session: dict, user_input: str) -> str:
        """Handle user response to alternative doctor offer"""
        if user_input.lower() in ['yes', 'y', 'ok', 'sure']:
            # User wants to see alternative doctors
            alternative_doctors = session.get('alternative_doctors', [])
            if not alternative_doctors:
                clear_session(session_id)
                return "Sorry, no alternative doctors available. Please try again later."
            
            # If only one alternative, auto-select it
            if len(alternative_doctors) == 1:
                doctor_id = alternative_doctors[0][0]
                doctor_name = alternative_doctors[0][1]
                
                session['doctor_id'] = doctor_id
                session['doctor_name'] = doctor_name
                
                # Get available slots for this doctor
                available_slots = get_available_slots(doctor_id)
                
                if not available_slots:
                    clear_session(session_id)
                    return f"Sorry, {doctor_name} has no available slots at the moment. Please try again later. Thank you!"
                
                # Use the first available slot
                first_slot = available_slots[0]
                session['date'] = str(first_slot[0])
                session['time'] = str(first_slot[1])
                
                session['state'] = ConversationState.CHECKING_AVAILABILITY.value
                save_session(session_id, session)
                
                return f"Great! {doctor_name} is available on {first_slot[0]} at {first_slot[1]}. Is that fine?"
            else:
                # Multiple alternatives - ask user to choose
                alt_names = " / ".join([doc[1] for doc in alternative_doctors])
                session['state'] = ConversationState.SELECTING_DOCTOR.value
                save_session(session_id, session)
                return f"Please select from: {alt_names}"
        else:
            # User doesn't want alternative, close session
            clear_session(session_id)
            return "Thank you for contacting us. Please try again later. Have a great day!"
    
    def handle_availability(self, session_id: str, session: dict, user_input: str) -> str:
        if user_input.lower() in ['yes', 'y', 'ok', 'fine', 'sure']:
            session['state'] = ConversationState.COLLECTING_PATIENT_DETAILS.value
            save_session(session_id, session)
            return "Great! May I have your name and contact number?"
        else:
            # User declined the offered slot, check for other slots
            doctor_id = session.get('doctor_id')
            doctor_name = session.get('doctor_name', 'the doctor')
            current_date = session.get('date')
            current_time = session.get('time')
            
            if not doctor_id:
                clear_session(session_id)
                return "Sorry, something went wrong. Please start over."
            
            # Track rejected slots
            if 'rejected_slots' not in session:
                session['rejected_slots'] = []
            
            # Add current slot to rejected list
            if current_date and current_time:
                rejected_slot = f"{current_date}|{current_time}"
                if rejected_slot not in session['rejected_slots']:
                    session['rejected_slots'].append(rejected_slot)
            
            # Get all available slots for this doctor
            available_slots = get_available_slots(doctor_id)
            
            # Filter out all rejected slots
            other_slots = []
            for slot in available_slots:
                slot_key = f"{str(slot[0])}|{str(slot[1])}"
                if slot_key not in session['rejected_slots']:
                    other_slots.append(slot)
            
            if other_slots:
                # Offer the next available slot
                next_slot = other_slots[0]
                session['date'] = str(next_slot[0])
                session['time'] = str(next_slot[1])
                save_session(session_id, session)
                
                return f"How about {next_slot[0]} at {next_slot[1]}? Is that fine?"
            else:
                # No other slots available
                clear_session(session_id)
                return f"Sorry, {doctor_name} has no other available slots at the moment. Please try again later or start a new booking. Thank you!"
    
    

    
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
    
    
    
    
    