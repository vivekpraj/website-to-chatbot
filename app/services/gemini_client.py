import os
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("Missing GEMINI_API_KEY environment variable")

# Create new Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_answer(prompt: str) -> str:
    """
    Sends prompt to Gemini 2.0 Flash using new google-genai SDK.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise
