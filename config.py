import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "default_model": "gpt-4o-2024-08-06",
    "temperature": 0.1,
}

MISTRAL_CONFIG = {
    "api_key": os.getenv("MISTRAL_API_KEY"),
    "default_model": "open-mistral-7b",
    "temperature": 0.1,
}

GEMINI_CONFIG = {
    "api_key" : os.getenv("GEMINI_API_KEY"),
    "default_model": "gemini-1",
    "temperature": 0.1,
}

OLLAMA_CONFIG = {
    "api_key": os.getenv("OLLAMA_API_KEY"),
    "default_model": "mistral",
    "temperature": 0.1}

