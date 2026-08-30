import argparse
import sys
import logging

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import Config
from sources.weather import get_weather_forecast
from sources.news import fetch_rss_news, fetch_community_discussions
from ai_summarizer import generate_daily_briefing
from notifiers.telegram_notifier import send_telegram_message

from subscribers import get_active_subscribers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DailyBriefingBot")

def dispatch_single_briefing(subscriber: dict, news_items: list, community_items: list, weather_cache: dict, dry_run: bool = False) -> bool:
    name = subscriber.get("name", "Friend")
    chat_id = subscriber.get("chat_id") or Config.TELEGRAM_CHAT_ID
    city = subscriber.get("city", Config.USER_CITY)
    topics = subscriber.get("topics", Config.FOCUS_TOPICS)

    # Fetch/cache weather
    if city not in weather_cache:
        logger.info(f"🌤️ Fetching weather for {city} ({name})...")
        weather_cache[city] = get_weather_forecast(city)
    weather = weather_cache[city]

    # Generate personalized briefing with Gemini
    logger.info(f"🧠 Generating personalized AI briefing for {name} [{chat_id}] [Topics: {', '.join(topics)}]...")
    briefing = generate_daily_briefing(
        user_name=name,
        city_weather=weather,
        news_items=news_items,
        reddit_items=community_items,
        focus_topics=topics,
        api_key=Config.GEMINI_API_KEY
    )

    if dry_run:
        print("\n" + "=" * 50)
        print(f"📋 PREVIEW FOR {name.upper()} [{chat_id}]:")
        print("=" * 50)
        print(briefing)
        print("=" * 50 + "\n")
        return True

    tg_success = False

    if Config.TELEGRAM_BOT_TOKEN:
        if chat_id:
            logger.info(f"✈️ Dispatching to {name} on Telegram (chat_id: {chat_id})...")
            tg_success = send_telegram_message(
                bot_token=Config.TELEGRAM_BOT_TOKEN,
                chat_id=chat_id,
                message=briefing
            )
        else:
            logger.error(f"No Telegram chat_id available for {name}. Skipping.")

    return tg_success

def run(dry_run: bool = False, custom_city: str = None, custom_name: str = None,
        target_chat_id: str = None) -> bool:
    logger.info("🌅 Starting Daily AI Briefing Pipeline...")

    # Validate settings if not running dry-run
    validation_errors = Config.validate(dry_run=dry_run, target_chat_id=target_chat_id)
    if validation_errors:
        logger.error("Configuration errors found:")
        for err in validation_errors:
            logger.error(f"  - {err}")
        logger.info("💡 Hint: Update your .env file or run with --dry-run to test locally.")
        return False

    # Step 1: Fetch Shared News & Community Trends
    logger.info("📰 Fetching global tech news feeds...")
    news_items = fetch_rss_news(Config.RSS_FEEDS, max_items_per_feed=4)
    logger.info(f"Collected {len(news_items)} news articles.")

    logger.info("🤖 Fetching community trends (Hacker News / Reddit)...")
    community_items = fetch_community_discussions(max_items=6)
    logger.info(f"Collected {len(community_items)} community discussions.")

    weather_cache = {}

    # Step 2: Determine recipients
    subscribers = get_active_subscribers()

    if target_chat_id:
        subscribers = [s for s in subscribers if s.get("chat_id") == target_chat_id]
        if not subscribers:
            subscribers = [{
                "name": custom_name or Config.USER_NAME,
                "chat_id": target_chat_id,
                "city": custom_city or Config.USER_CITY,
                "topics": Config.FOCUS_TOPICS,
                "channel": Config.NOTIFICATION_CHANNEL
            }]

    if not subscribers:
        logger.info("No subscribers found. Using .env default recipient.")
        subscribers = [{
            "name": custom_name or Config.USER_NAME,
            "chat_id": Config.TELEGRAM_CHAT_ID,
            "city": custom_city or Config.USER_CITY,
            "topics": Config.FOCUS_TOPICS,
            "channel": Config.NOTIFICATION_CHANNEL
        }]

    logger.info(f"👥 Found {len(subscribers)} active recipient(s) to process.")

    # Step 3: Dispatch to each recipient
    sent_count = 0
    for sub in subscribers:
        try:
            ok = dispatch_single_briefing(
                subscriber=sub,
                news_items=news_items,
                community_items=community_items,
                weather_cache=weather_cache,
                dry_run=dry_run
            )
            if ok:
                sent_count += 1
        except Exception as e:
            logger.error(f"Error dispatching to {sub.get('name', 'User')}: {e}")

    logger.info(f"🎉 Daily briefing dispatch complete! Sent: {sent_count}/{len(subscribers)}")
    return sent_count > 0 or dry_run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Daily Briefing AI Bot")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without sending messages (prints briefing to terminal)."
    )
    parser.add_argument("--city", type=str, help="Override city for weather forecast.")
    parser.add_argument("--name", type=str, help="Override recipient name.")
    parser.add_argument("--chat-id", type=str, help="Target a specific Telegram chat ID.")

    args = parser.parse_args()
    success = run(
        dry_run=args.dry_run,
        custom_city=args.city,
        custom_name=args.name,
        target_chat_id=args.chat_id
    )
    if not success:
        sys.exit(1)
