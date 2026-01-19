from uuid import uuid4
from orchestrator import ConversationOrchestrator

session_id = uuid4().hex
bot = ConversationOrchestrator()

print("Bot: Hello and welcome to the Super Clinic")

while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    response = bot.handle(session_id, user_input)
    print("Bot:", response)
