import os
from dotenv import load_dotenv
from openai import OpenAI
import time

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(messages, functions=None):
    params = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    if functions:
        params["functions"] = functions
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**params)
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)