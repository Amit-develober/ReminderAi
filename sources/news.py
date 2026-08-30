import feedparser
import requests
import logging
import re
import html
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def _clean_html_text(text: str) -> str:
    """Removes HTML tags, scripts, styles, and unescapes entities."""
    if not text:
        return ""
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", text)
    # Unescape HTML entities (e.g. &amp; -> &, &quot; -> ")
    cleaned = html.unescape(cleaned)
    # Collapse multiple whitespace/newlines
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def fetch_rss_news(feeds: List[Dict[str, str]], max_items_per_feed: int = 3) -> List[Dict[str, str]]:
    """
    Fetches latest articles from a list of RSS feeds.
    Each feed dict should have {"name": "Feed Name", "url": "Feed URL"}.
    """
    news_items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DailyBriefingBot/1.0"}

    for feed in feeds:
        name = feed.get("name", "Unknown Source")
        url = feed.get("url", "")
        if not url:
            continue

        try:
            # Fetch with custom headers to prevent 403 Forbidden on some feeds
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200:
                parsed = feedparser.parse(resp.content)
            else:
                parsed = feedparser.parse(url)

            entries = parsed.entries[:max_items_per_feed]
            for entry in entries:
                title = _clean_html_text(getattr(entry, "title", ""))
                link = getattr(entry, "link", "").strip()
                summary_raw = getattr(entry, "summary", "") or getattr(entry, "description", "")
                summary = _clean_html_text(summary_raw)
                
                # Truncate summary if excessively long
                if len(summary) > 280:
                    summary = summary[:280] + "..."

                if title:
                    news_items.append({
                        "source": name,
                        "title": title,
                        "summary": summary,
                        "link": link
                    })
        except Exception as e:
            logger.warning(f"Failed to fetch RSS feed '{name}': {e}")
            continue

    return news_items


def fetch_community_discussions(max_items: int = 5) -> List[Dict[str, str]]:
    """
    Fetches trending community discussions from Hacker News API (100% free, no key or rate limits)
    and Reddit RSS feeds.
    """
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DailyBriefingBot/1.0"}

    # 1. Fetch top discussions from Hacker News Official API
    try:
        top_ids_resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=6)
        if top_ids_resp.status_code == 200:
            top_ids = top_ids_resp.json()[:max_items]
            for item_id in top_ids:
                try:
                    item_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=4)
                    if item_resp.status_code == 200:
                        item_data = item_resp.json()
                        if not item_data:
                            continue
                        title = _clean_html_text(item_data.get("title", ""))
                        url = item_data.get("url") or f"https://news.ycombinator.com/item?id={item_id}"
                        score = item_data.get("score", 0)
                        comments = item_data.get("descendants", 0)

                        if title:
                            items.append({
                                "source": "Hacker News",
                                "title": title,
                                "summary": f"{score} points | {comments} comments",
                                "link": url
                            })
                except Exception:
                    continue
    except Exception as e:
        logger.warning(f"Failed to fetch Hacker News API: {e}")

    # 2. Reddit RSS fallback
    for sub in ["artificial", "technology"]:
        if len(items) >= max_items + 3:
            break
        try:
            feed_url = f"https://www.reddit.com/r/{sub}/hot/.rss?limit=3"
            resp = requests.get(feed_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                parsed = feedparser.parse(resp.content)
                for entry in parsed.entries[:2]:
                    title = _clean_html_text(getattr(entry, "title", ""))
                    link = getattr(entry, "link", "").strip()
                    if title:
                        items.append({
                            "source": f"r/{sub}",
                            "title": title,
                            "summary": f"Discussion from r/{sub}",
                            "link": link
                        })
        except Exception:
            continue

    return items


