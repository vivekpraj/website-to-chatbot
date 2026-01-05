import os
import logging
from google import genai
from google.genai.errors import ClientError

logger = logging.getLogger(__name__)

class GeminiQuotaError(Exception):
    pass

# Get API key - works in both local and CI environments
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "dummy-key")

# Initialize client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.warning(f"Could not initialize Gemini client: {e}")
    client = None

def generate_answer(prompt: str) -> str:
    """
    Sends prompt to Gemini 2.0 Flash using new google-genai SDK.
    """
    if not client or GEMINI_API_KEY == "dummy-key":
        raise Exception("GEMINI_API_KEY not configured properly")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except ClientError as e:
        logger.error(f"Gemini quota error: {e}")
        raise GeminiQuotaError("AI service quota exceeded")
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise