from uuid import uuid4
from app.orchestrator import ConversationOrchestrator

session_id = uuid4().hex
bot = ConversationOrchestrator()

print("Bot: Hello and welcome to the Super Clinic")

while True:
    user_input = input("User: ")
    if len(user_input.strip()) > 500:
        response = "Could you please describe briefly."
    elif user_input.lower() in ["exit", "quit"]:
        break
    else:
        response = bot.handle(session_id, user_input)
    print("Bot:", response)
