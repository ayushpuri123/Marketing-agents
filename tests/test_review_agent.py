"""
Tests for agents/review_agent.py.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.review_agent import run
from agents.analytics_agent import run as run_analytics


SAMPLE_BRIEF = {
    "business_name": "Riverside Yoga Studio",
    "industry": "Fitness",
    "product": "Beginner yoga classes",
    "audience": "Busy professionals aged 25-40",
    "objective": "Increase new class sign-ups",
    "channel": "Instagram",
    "tone": "Calm and encouraging",
    "budget_level": "Low",
    "notes": "",
}


def test_review_agent_detects_unsupported_claims():
    content = {
        "hook": "Studies show 95% of customers love our classes!",
        "caption": "Riverside Yoga Studio is the #1 studio in town.",
        "cta": "Book your first class today for $10.",
        "video_idea": "A calm flow sequence.",
    }
    result = run(SAMPLE_BRIEF, research=None, content=content, analytics=None)
    assert result["status"] == "Problem Found"
    assert any("Unsupported claim" in f for f in result["findings"])


def test_review_agent_detects_recommendation_inconsistent_with_data():
    # Build a real KPI result, then deliberately corrupt the recommendation
    # to simulate drift/a bug/a manual edit — exactly what this check exists to catch.
    analytics = run_analytics({
        "impressions": 10000, "clicks": 600, "spend": 1000,
        "conversions": 20, "revenue": 400,   # ROAS = 0.4 -> should be "Pause"
    })
    analytics["recommendation"] = "Keep"  # corrupted on purpose

    result = run(SAMPLE_BRIEF, research=None, content=None, analytics=analytics)
    assert result["status"] == "Problem Found"
    assert any("inconsistency" in f.lower() for f in result["findings"])


def test_review_agent_passes_consistent_recommendation():
    analytics = run_analytics({
        "impressions": 10000, "clicks": 600, "spend": 1000,
        "conversions": 20, "revenue": 400,
    })
    # Recommendation left untouched, so it IS consistent with the ROAS.
    result = run(SAMPLE_BRIEF, research=None, content=None, analytics=analytics)
    assert result["status"] == "Pass"


def test_review_agent_flags_vague_cta():
    content = {
        "hook": "Feeling stressed?",
        "caption": "Come try a class at Riverside Yoga Studio.",
        "cta": "Learn more",
        "video_idea": "A calm flow sequence.",
    }
    result = run(SAMPLE_BRIEF, research=None, content=content, analytics=None)
    assert result["status"] in ("Needs Review", "Problem Found")
    assert any("Vague CTA" in f for f in result["findings"])


def test_review_agent_clean_content_passes():
    content = {
        "hook": "New to yoga? Riverside Yoga Studio has a beginner class for you.",
        "caption": "Join Riverside Yoga Studio's beginner yoga classes this week.",
        "cta": "Book your beginner class at Riverside Yoga Studio today.",
        "video_idea": "A calm flow sequence for first-timers.",
    }
    result = run(SAMPLE_BRIEF, research=None, content=content, analytics=None)
    assert result["status"] == "Pass"
