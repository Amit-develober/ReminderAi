"""
API routes for the AI Email Action Manager.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.db import get_db
from backend.database import crud
from backend.services.demo_data import get_demo_emails, get_demo_stats
from backend.utils.helpers import get_greeting, get_deadline_section
from backend.models.schemas import DashboardStats

router = APIRouter(prefix="/api", tags=["api"])


# ─── Demo Mode Endpoints ─────────────────────────────────────

@router.get("/demo/emails")
def get_demo_email_list():
    """Get all demo emails with analysis."""
    emails = get_demo_emails()
    result = []
    for i, email in enumerate(emails):
        result.append({
            "id": i + 1,
            "gmail_message_id": email["gmail_message_id"],
            "thread_id": email["thread_id"],
            "sender": email["sender"],
            "sender_email": email["sender_email"],
            "subject": email["subject"],
            "received_at": email["received_at"],
            "is_read": email["is_read"],
            "analysis": email["analysis"]
        })
    return {"emails": result}


@router.get("/demo/emails/{email_id}")
def get_demo_email_detail(email_id: int):
    """Get a specific demo email with full details."""
    emails = get_demo_emails()
    if email_id < 1 or email_id > len(emails):
        raise HTTPException(status_code=404, detail="Email not found")
    email = emails[email_id - 1]
    return {
        "id": email_id,
        **email
    }


@router.get("/demo/dashboard")
def get_demo_dashboard():
    """Get demo dashboard data — actions grouped by priority."""
    emails = get_demo_emails()
    greeting = get_greeting()

    actions_by_priority = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for i, email in enumerate(emails):
        analysis = email["analysis"]
        if analysis["action_required"]:
            action_item = {
                "id": i + 1,
                "email_id": i + 1,
                "sender": email["sender"],
                "subject": email["subject"],
                "action_text": analysis["action"],
                "priority": analysis["priority"],
                "deadline": analysis.get("deadline"),
                "deadline_relative": _format_demo_deadline(analysis.get("deadline")),
                "summary": analysis["summary"],
                "status": "pending"
            }
            if analysis["priority"] in actions_by_priority:
                actions_by_priority[analysis["priority"]].append(action_item)

    stats = get_demo_stats()

    return {
        "greeting": greeting,
        "message": "Here's what needs your attention.",
        "actions_by_priority": actions_by_priority,
        "stats": stats,
        "is_demo": True
    }


@router.get("/demo/actions")
def get_demo_actions():
    """Get demo actions grouped by deadline section."""
    emails = get_demo_emails()

    sections = {
        "overdue": [],
        "today": [],
        "tomorrow": [],
        "this_week": [],
        "no_deadline": []
    }

    for i, email in enumerate(emails):
        analysis = email["analysis"]
        if analysis["action_required"]:
            section = get_deadline_section(analysis.get("deadline"))
            action_item = {
                "id": i + 1,
                "email_id": i + 1,
                "sender": email["sender"],
                "subject": email["subject"],
                "action_text": analysis["action"],
                "priority": analysis["priority"],
                "deadline": analysis.get("deadline"),
                "summary": analysis["summary"],
                "category": analysis["category"],
                "status": "pending"
            }
            if section in sections:
                sections[section].append(action_item)
            else:
                sections["no_deadline"].append(action_item)

    return {"sections": sections, "is_demo": True}


@router.get("/demo/stats")
def get_demo_statistics():
    """Get demo statistics."""
    return get_demo_stats()


# ─── Health Check ─────────────────────────────────────────────

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI Email Action Manager is running"}


# ─── User Session (placeholder for auth stages) ──────────────

@router.get("/me")
def get_current_user(request: Request):
    """Get current user info. Returns demo user if in demo mode."""
    # For now, return demo mode info
    # Will be replaced with real auth in Stage 4
    return {
        "is_demo": True,
        "user": {
            "name": "Demo User",
            "email": "demo@example.com",
            "picture": None,
            "gmail_connected": True
        }
    }


# ─── Helper ──────────────────────────────────────────────────

def _format_demo_deadline(date_str):
    """Format deadline for demo display."""
    from backend.utils.helpers import format_relative_date
    return format_relative_date(date_str) if date_str else "No deadline"
