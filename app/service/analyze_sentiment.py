import json
from google import genai
from app.config import settings
import logging
logger = logging.getLogger(__name__)

GEMINI_API_KEY = settings.GEMINI_API_KEY
client = genai.Client()

async def analyze_text(text: str):
    """
    Analyze a given text: generate a summary and detect sentiment.
    Returns: summary (str), sentiment (str: Positive/Negative/Neutral)
    """
    prompt = f"""
    You are an assistant. Summarize the following text in 2-3 sentences and detect its sentiment as Positive, Negative, or Neutral.

    Text:
    {text}

    Format your response as JSON like:
    {{
        "summary": "<your summary>",
        "sentiment": "<Positive/Negative/Neutral>"
    }}
    """

    try:
        logger.info(f"Analyzing text with Gemini API: {text}")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw_txt = response.text

        # Extract JSON safely
        start = raw_txt.find("{")
        end = raw_txt.rfind("}") + 1
        json_str = raw_txt[start:end]

        data = json.loads(json_str)
        logger.info(f"Gemini response data: {data}")
        summary = data.get("summary", "")
        logger.info(f"Summary extracted: {summary}")
        sentiment = data.get("sentiment", "Neutral")
        logger.info(f"Sentiment extracted: {sentiment}")
        return summary, sentiment

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return "", "Neutral"
