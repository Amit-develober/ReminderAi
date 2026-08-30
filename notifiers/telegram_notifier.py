import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Sends a formatted message to a specific Telegram chat/channel using the Telegram Bot API.
    Handles message splitting if exceeding Telegram's 4096 character limit,
    and falls back to plain text if Markdown parsing errors occur.
    """
    if not bot_token or not chat_id:
        logger.error("Cannot send Telegram message: Bot token or Chat ID is missing.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Telegram max message length is 4096 characters
    max_len = 4000
    chunks = [message[i:i + max_len] for i in range(0, len(message), max_len)]

    success = True
    for chunk in chunks:
        # Try sending with Markdown formatting first
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json()

            if not data.get("ok"):
                logger.warning(f"Telegram Markdown parse failed ({data.get('description')}). Retrying as plain text...")
                # Retry without parse_mode
                payload.pop("parse_mode", None)
                retry_resp = requests.post(url, json=payload, timeout=15)
                retry_data = retry_resp.json()
                if not retry_data.get("ok"):
                    logger.error(f"Failed to send Telegram message: {retry_data}")
                    success = False
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            success = False

    return success
