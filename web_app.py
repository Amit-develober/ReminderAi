import os
import logging
import threading
from flask import Flask, render_template, request, jsonify
from subscribers import (
    load_subscribers,
    add_or_update_subscriber,
    unsubscribe,
    get_active_subscribers,
)
from main import run as run_briefing_pipeline
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("WebApp")

app = Flask(__name__)

@app.route("/")
def index():
    active_count = len(get_active_subscribers())
    return render_template("index.html", active_count=active_count)

# ---------------------------------------------------------------------------
# Subscription endpoints
# ---------------------------------------------------------------------------

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    try:
        data = request.get_json() or {}
        name     = data.get("name", "").strip() or "Friend"
        chat_id  = data.get("chat_id", "").strip()   # Telegram Chat ID (primary)
        city     = data.get("city", "").strip() or "New York"
        topics   = data.get("topics", [])

        if not chat_id:
            return jsonify({"success": False, "error": "Telegram Chat ID is required."}), 400

        if not topics:
            topics = ["AI & Tech", "Business", "World News"]

        sub = add_or_update_subscriber(
            name=name,
            chat_id=chat_id,
            city=city,
            topics=topics
        )

        identifier = sub.get("chat_id")
        return jsonify({
            "success": True,
            "message": (
                f"🎉 Successfully subscribed {sub['name']} (ID: {identifier})! "
                f"You will receive your daily brief every morning at 8:00 AM."
            ),
            "subscriber": sub
        })
    except Exception as e:
        logger.error(f"Error subscribing: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/unsubscribe", methods=["POST"])
def api_unsubscribe():
    """Unsubscribes a user by Telegram chat_id."""
    try:
        data = request.get_json() or {}
        identifier = data.get("chat_id", "").strip()

        if not identifier:
            return jsonify({"success": False, "error": "chat_id is required."}), 400

        ok = unsubscribe(identifier)
        if ok:
            return jsonify({"success": True, "message": f"Successfully unsubscribed {identifier} from daily briefings."})
        else:
            return jsonify({"success": False, "error": f"No active subscription found for {identifier}."}), 404
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/test-dispatch", methods=["POST"])
def test_dispatch():
    """Sends an instant sample briefing to the requested Telegram chat."""
    try:
        data = request.get_json() or {}
        name    = data.get("name", "").strip() or "Friend"
        chat_id = data.get("chat_id", "").strip()
        city    = data.get("city", "").strip() or "New York"
        topics  = data.get("topics", ["AI & Tech", "Business"])

        if not chat_id:
            return jsonify({"success": False, "error": "Telegram Chat ID is required."}), 400

        # Save subscriber, then run pipeline async
        sub = add_or_update_subscriber(
            name=name,
            chat_id=chat_id,
            city=city,
            topics=topics
        )
        target_chat = sub.get("chat_id") or Config.TELEGRAM_CHAT_ID

        def send_async():
            try:
                run_briefing_pipeline(
                    dry_run=False,
                    custom_city=city,
                    custom_name=name,
                    target_chat_id=target_chat
                )
            except Exception as ex:
                logger.error(f"Async test dispatch error: {ex}")

        threading.Thread(target=send_async, daemon=True).start()

        identifier = target_chat or name
        return jsonify({
            "success": True,
            "message": f"🚀 Instant briefing is being generated and sent to Telegram ({identifier}) right now!"
        })
    except Exception as e:
        logger.error(f"Error in test dispatch: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/subscribers", methods=["GET"])
def list_subscribers():
    subs = load_subscribers()
    safe_subs = []
    for s in subs:
        raw_chat = s.get("chat_id", "")
        # Mask identifiers for privacy
        masked_chat = raw_chat[:4] + "***" if len(raw_chat) > 4 else raw_chat
        safe_subs.append({
            "name": s.get("name"),
            "chat_id": masked_chat,
            "city": s.get("city"),
            "topics": s.get("topics"),
            "active": s.get("active", True),
            "subscribed_at": s.get("subscribed_at")
        })
    return jsonify({"success": True, "count": len(safe_subs), "subscribers": safe_subs})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n✨ Daily Briefing Web Portal running at: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
