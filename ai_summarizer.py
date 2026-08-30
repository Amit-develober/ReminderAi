import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

def generate_daily_briefing(
    user_name: str,
    city_weather: Optional[Dict[str, Any]],
    news_items: List[Dict[str, str]],
    reddit_items: List[Dict[str, str]],
    focus_topics: List[str],
    api_key: str,
    model_name: str = "gemini-2.5-flash"
) -> str:
    """
    Uses the official Google GenAI SDK to synthesize news, weather, and topics
    into an executive morning briefing formatted for Telegram Markdown.
    """
    date_str = datetime.now().strftime("%A, %B %d, %Y")
    
    weather_text = "Weather data unavailable."
    if city_weather:
        weather_text = (
            f"City: {city_weather.get('city')}\n"
            f"Condition: {city_weather.get('condition')}\n"
            f"Current Temperature: {city_weather.get('current_temp')} (Feels like {city_weather.get('feels_like')})\n"
            f"High / Low: {city_weather.get('temp_max')} / {city_weather.get('temp_min')}\n"
            f"Rain Probability: {city_weather.get('rain_probability')}"
        )

    news_text = ""
    for i, item in enumerate(news_items, 1):
        news_text += f"{i}. [{item['source']}] {item['title']}\n   Summary: {item['summary']}\n   URL: {item['link']}\n"

    community_text = ""
    for i, item in enumerate(reddit_items, 1):
        community_text += f"{i}. [{item['source']}] {item['title']} ({item['summary']})\n   URL: {item['link']}\n"

    system_instruction = (
        "You are an executive AI assistant creating an ultra-concise, bite-sized daily morning briefing for WhatsApp.\n"
        "Rules:\n"
        "1. Keep it SHORT, punchy, and easy to skim in 20 seconds.\n"
        "2. Start with a 1-line greeting with the user's name and date.\n"
        "3. Include a 1-line quick weather update & outfit tip.\n"
        "4. Include ONLY the top 3 most important stories.\n"
        "5. For each story: provide a bold title followed immediately by ONE crisp, informative sentence. (e.g. *• Google Slashes AI Token Usage:* New research shows 94% cost reduction for long-running agents.)\n"
        "6. STRICTLY DO NOT include ANY website links, URLs, or source links (no 'https://', no 'TechCrunch (http...)', etc.). Keep it 100% link-free.\n"
        "7. End with a 1-line inspiring thought for the day.\n"
        "8. Use clean WhatsApp formatting (bold with *)."
    )

    prompt = f"""
{system_instruction}

--- USER PREFERENCES & FOCUS TOPICS ---
Name: {user_name}
Date: {date_str}
Focus Interests: {', '.join(focus_topics)}

--- REAL-TIME WEATHER ---
{weather_text}

--- LATEST NEWS HEADLINES ---
{news_text if news_text else "No news fetched."}

--- TRENDING COMMUNITY DISCUSSIONS ---
{community_text if community_text else "No community posts fetched."}

Generate the short, link-free WhatsApp morning brief now:
"""

    clean_key = (api_key or "").strip()
    if not clean_key:
        logger.warning("No Gemini API key provided. Generating mock preview briefing.")
        return generate_mock_briefing(user_name, date_str, city_weather, news_items)

    try:
        client = genai.Client(api_key=clean_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        if response and response.text:
            text = response.text.strip()
            # Normalize any double-asterisk bold to WhatsApp single-asterisk
            text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
            return text
        else:
            logger.warning("Empty response from Gemini. Falling back to preview.")
            return generate_mock_briefing(user_name, date_str, city_weather, news_items)

    except Exception as e:
        logger.error(f"Gemini API request with {model_name} failed: {e}")
        # Try fallback model
        for fallback in ["gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                client = genai.Client(api_key=clean_key)
                response = client.models.generate_content(
                    model=fallback,
                    contents=prompt,
                )
                if response and response.text:
                    text = response.text.strip()
                    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
                    return text
            except Exception:
                continue

        return generate_mock_briefing(user_name, date_str, city_weather, news_items)


def generate_mock_briefing(user_name: str, date_str: str, city_weather: Optional[Dict[str, Any]], news_items: List[Dict[str, str]]) -> str:
    """Generates a fallback briefing when offline or testing without API key."""
    weather_line = "☀️ *Weather:* Mild with clear skies."
    if city_weather:
        weather_line = f"☀️ *Weather:* {city_weather['condition']} | {city_weather['current_temp']} in {city_weather['city']}."

    headlines = ""
    for item in news_items[:3]:
        headlines += f"• *{item['title']}:* Top development in tech.\n"

    return f"""Good morning, {user_name}! 🚀 {date_str}

{weather_line}

*Today's Highlights:*
{headlines if headlines else "• *No top stories collected today.*\n"}
✨ *Thought for the Day:* "The secret of getting ahead is getting started."
"""
