import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Config:
    # AI Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    
    # Notification Channel Selector (Only telegram is supported now)
    NOTIFICATION_CHANNEL = "telegram"

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    # User Preferences
    USER_CITY = os.getenv("USER_CITY", "New York").strip()
    USER_NAME = os.getenv("USER_NAME", "Friend").strip()
    FOCUS_TOPICS = [
        topic.strip() 
        for topic in os.getenv("FOCUS_TOPICS", "AI & Tech, Business, World News").split(",") 
        if topic.strip()
    ]
    
    # Default RSS feeds to collect news from
    RSS_FEEDS = [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "BBC World News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    ]

    @classmethod
    def validate(cls, dry_run: bool = False, target_chat_id: str = None):
        """Check if necessary variables are populated for execution."""
        errors = []
        if not dry_run:
            if not cls.GEMINI_API_KEY:
                errors.append("GEMINI_API_KEY is not set.")

            if not cls.TELEGRAM_BOT_TOKEN:
                errors.append("TELEGRAM_BOT_TOKEN is missing in .env.")
                    
        return errors
