import os
import google.generativeai as genai

def get_llm_model():
    """Configures and returns the Gemini GenerativeModel"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file")

    genai.configure(api_key=api_key)
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    return genai.GenerativeModel(model_name)
