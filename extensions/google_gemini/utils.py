from config import CONFIG

from google import genai



def _chat_completion_endpoint(content: str) -> str:
    client = genai.Client(api_key=CONFIG["google_gemini"]["api_key"])

    response = client.models.generate_content(
        model=CONFIG["google_gemini"]["default_model"], 
        contents=content
    )

    return response.text
