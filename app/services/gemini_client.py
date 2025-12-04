import google.generativeai as genai
import os

# Load Gemini API key
GEMINI_API_KEY = os.getenv("AIzaSyBdkEuxj9W4Cex532hLctE1Z_IFPY6kPvI")

if not GEMINI_API_KEY:
    raise Exception("Missing GEMINI_API_KEY env variable")

genai.configure(api_key=GEMINI_API_KEY)


def generate_answer(prompt: str) -> str:
    """
    Send RAG prompt to Gemini model and return the response text.
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return response.text
