# Doctor's Assistant Chatbot

An intelligent chatbot system for booking doctor appointments at Super Clinic. The system uses AI to understand symptoms, infer medical specialties, and manage the complete appointment booking workflow.

## Features

- 🤖 **AI-Powered Specialty Detection** - Uses OpenAI GPT to infer medical specialty from symptoms
- 📅 **Smart Slot Management** - Finds and offers available appointment slots
- 🔄 **Alternative Doctor Suggestions** - Offers alternative doctors when first choice is unavailable
- 💾 **Session Management** - Supports both Redis and in-memory session storage
- 🗄️ **PostgreSQL Database** - Stores doctors, schedules, patients, and appointments
- 🌐 **REST API** - FastAPI-based RESTful API with automatic documentation
- ✅ **Comprehensive Validation** - Handles edge cases and invalid inputs gracefully

## Architecture

```
doctors_assistant/
├── app/
│   ├── api/              # FastAPI endpoints
│   ├── services/         # Business logic services
│   ├── orchestrator.py   # Conversation state management
│   ├── llm_client.py     # OpenAI integration
│   ├── session_store*.py # Session management (Redis/Memory)
│   └── prompts.py        # AI prompts
├── db/
│   ├── connection.py     # Database connection
│   ├── schema.sql        # Database schema
│   ├── seed.sql          # Sample data
│   └── *_repo.py         # Data access layer
├── tests/                # Test cases
└── main.py              # CLI interface
```

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis (optional, for production)
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Satyanarayana06b/doctors_assistant.git
   cd doctors_assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Make sure `streamlit` is in your requirements.txt. If not, install it:
   ```bash
   pip install streamlit
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   
   # PostgreSQL
   DB_HOST=localhost
   DB_NAME=clinic
   DB_USER=admin
   DB_PASSWORD=admin
   
   # Redis (optional)
   USE_REDIS=false
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=
   ```

5. **Set up PostgreSQL database**
   ```bash
   # Run setup script (creates user, database, tables, and seed data)
   python tests/setup_database.py
   ```
   
   Or manually:
   ```bash
   psql -U postgres -f db/schema.sql
   psql -U postgres -f db/seed.sql
   ```

## Usage

### Streamlit Web Interface (Recommended)

The easiest way to interact with the chatbot is through the Streamlit web interface.

1. **Start the API server** (in one terminal)
   ```bash
   uvicorn main_api:app --reload
   ```

2. **Start Streamlit** (in another terminal)
   ```bash
   streamlit run app/ui/streamlit_app.py
   ```

3. **Access the chat interface**
   - Open your browser to http://localhost:8501
   - Start chatting with the doctor's assistant!

**Features:**
- 💬 Clean chat interface
- 🔄 Session persistence
- 📱 Mobile-friendly design
- ⚡ Real-time responses

### Command Line Interface

```bash
python main.py
```

**Example conversation:**
```
Bot: Hello and welcome to the Super Clinic
User: Hi
Bot: Hello! Please describe your health issue?
User: I have knee pain
Bot: Thank you. Which doctor would you like to meet? (Dr X / Dr Y)
User: Dr X
Bot: Dr X is available on 2026-01-22 at 11:00:00. Is that fine?
User: yes
Bot: Great! May I have your name and contact number?
User: John Doe 1234567890
Bot: Perfect! Your appointment with Dr X (Orthopedics) is confirmed for 2026-01-22 at 11:00:00...
```

### REST API (Advanced Users)

For direct API integration or custom frontends:

1. **Start the API server**
   ```bash
   uvicorn main_api:app --reload
   ```

2. **Access the API**
   - API Documentation: http://127.0.0.1:8000/docs
   - Chat Endpoint: `POST http://127.0.0.1:8000/api/chat`

3. **Example API request**
   ```json
   {
     "session_id": "optional-session-id",
     "message": "I have fever"
   }
   ```

**Note:** The Streamlit app uses this API backend, so both need to be running for the web interface to work.

## Conversation Flow

```
INIT
  ↓
COLLECTING_SYMPTOMS (AI infers specialty)
  ↓
SELECTING_DOCTOR
  ↓
[If doctor unavailable] → OFFERING_ALTERNATIVE_DOCTOR
  ↓
CHECKING_AVAILABILITY
  ↓
[If slot rejected] → Offer next slot or end
  ↓
COLLECTING_PATIENT_DETAILS
  ↓
BOOKING CONFIRMED → Reset to INIT
```

## Database Schema

- **doctors** - Doctor information and specialty
- **doctor_schedules** - Available time slots
- **patients** - Patient contact information
- **appointments** - Booked appointments

## Configuration

### Session Storage

**In-Memory (Default):**
- Set `USE_REDIS=false` or omit it
- Best for development/testing

**Redis:**
- Set `USE_REDIS=true`
- Requires Redis server running
- Better for production (persistent sessions)

### Available Specialties

- Orthopedics
- Dermatology
- Cardiology
- Neurology
- Pediatrics
- General Medicine

## Testing

```bash
# Run booking scenario tests
python tests/test_booking_scenarios.py

# Test database connection
python tests/test_db_connection.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message and get bot response |
| `/docs` | GET | Interactive API documentation |

## Error Handling

The system gracefully handles:
- Invalid symptoms/inputs
- Unavailable doctors
- No available slots
- Double booking attempts
- LLM API failures (with retry)
- Database connection errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Contact

For questions or support, please contact the repository owner.

---

**Built with ❤️ using FastAPI, OpenAI, PostgreSQL, and Redis**
