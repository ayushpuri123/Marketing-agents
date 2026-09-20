import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.research_agent import run as run_research
from agents.content_agent import run as run_content
from agents.review_agent import run as run_review


BRIEF = {
    "business_name": "Riverside Yoga Studio",
    "industry": "Fitness",
    "product": "Beginner yoga classes",
    "audience": "Busy professionals aged 25-40",
    "objective": "Increase new class sign-ups",
    "channel": "Instagram",
    "tone": "Calm and encouraging",
    "budget_level": "Low",
    "notes": "No medical claims",
}


def test_research_is_local_and_labels_assumptions():
    result = run_research(BRIEF)
    assert result["_source"] == "local_deterministic"
    assert result["primary_audience"] == BRIEF["audience"]
    assert any("ASSUMPTION" in item for item in result["assumptions"])
    assert all("Placeholder" not in str(value) for value in result.values())


def test_content_is_specific_to_brief_and_channel():
    research = run_research(BRIEF)
    result = run_content(BRIEF, research)
    assert result["_source"] == "local_deterministic"
    assert BRIEF["business_name"] in result["caption"]
    assert BRIEF["product"].lower() in result["caption"].lower()
    assert "cta" in result


def test_clean_workflow_passes_review():
    research = run_research(BRIEF)
    content = run_content(BRIEF, research)
    result = run_review(BRIEF, research=research, content=content)
    assert result["status"] == "Pass"


def test_wrong_channel_shape_is_caught():
    bad_content = {
        "subject": "Email-shaped content on Instagram",
        "email_body": "Riverside Yoga Studio beginner yoga classes",
        "cta": "Book your beginner yoga class at Riverside Yoga Studio.",
    }
    result = run_review(BRIEF, content=bad_content)
    assert result["status"] == "Problem Found"
    assert any("Channel mismatch" in finding for finding in result["findings"])
