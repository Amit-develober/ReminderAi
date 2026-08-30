import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

SUBSCRIBERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscribers.json")

def load_subscribers() -> List[Dict[str, Any]]:
    """Loads all subscribers from subscribers.json."""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Error loading subscribers from {SUBSCRIBERS_FILE}: {e}")
        return []

def save_subscribers(subscribers: List[Dict[str, Any]]) -> bool:
    """Saves subscribers list to subscribers.json."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(SUBSCRIBERS_FILE)), exist_ok=True)
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(subscribers, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving subscribers to {SUBSCRIBERS_FILE}: {e}")
        return False

def get_active_subscribers() -> List[Dict[str, Any]]:
    """Returns only active subscribers."""
    all_subs = load_subscribers()
    return [s for s in all_subs if s.get("active", True)]

def add_or_update_subscriber(
    name: str,
    chat_id: str,
    city: str,
    topics: List[str]
) -> Dict[str, Any]:
    """
    Adds a new subscriber or updates an existing one matching the given chat_id (Telegram).
    """
    clean_chat_id = str(chat_id).strip() if chat_id else ""

    if not clean_chat_id:
        raise ValueError("chat_id (Telegram) is required.")

    subscribers = load_subscribers()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Clean topics
    clean_topics = [t.strip() for t in topics if t and t.strip()]
    if not clean_topics:
        clean_topics = ["AI & Tech", "Business", "World News"]

    existing = next((s for s in subscribers if s.get("chat_id") == clean_chat_id), None)
    if existing:
        existing["name"] = name.strip() or existing.get("name", "Friend")
        existing["city"] = city.strip() or existing.get("city", "New York")
        existing["topics"] = clean_topics
        existing["channel"] = "telegram"
        existing["active"] = True
        existing["updated_at"] = now_str
        save_subscribers(subscribers)
        logger.info(f"Updated subscriber: {clean_chat_id} ({existing['name']})")
        return existing
    else:
        new_sub = {
            "name": name.strip() or "Friend",
            "chat_id": clean_chat_id,
            "city": city.strip() or "New York",
            "topics": clean_topics,
            "channel": "telegram",
            "active": True,
            "subscribed_at": now_str
        }
        subscribers.append(new_sub)
        save_subscribers(subscribers)
        logger.info(f"Added new subscriber: {clean_chat_id} ({new_sub['name']})")
        return new_sub

def unsubscribe(chat_id: str) -> bool:
    """Deactivates a subscriber by chat_id (Telegram)."""
    if not chat_id:
        return False

    clean_chat_id = chat_id.strip()

    subscribers = load_subscribers()
    updated = False
    for s in subscribers:
        if s.get("chat_id") == clean_chat_id:
            s["active"] = False
            s["unsubscribed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = True

    if updated:
        save_subscribers(subscribers)
        logger.info(f"Unsubscribed: {clean_chat_id}")
        return True
    return False
