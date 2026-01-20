from fastapi import FastAPI
from app.api.chatbot import router as chatbot_router

app = FastAPI(title="Doctors Assistant Chatbot API", version="1.0.0")

app.include_router(chatbot_router, prefix="/api")