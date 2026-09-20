"""Tests for agents/analytics_agent.py."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.analytics_agent import run


def test_strong_roas_and_conversion_recommends_test():
    result = run({
        "impressions": 10000, "clicks": 400, "spend": 500,
        "conversions": 40, "revenue": 2500,
    })
    assert result["recommendation"] == "Test"
    assert "ROAS >=" in result["rule_triggered"]


def test_zero_conversions_handled_without_crash():
    result = run({
        "impressions": 5000, "clicks": 100, "spend": 200,
        "conversions": 0, "revenue": 0,
    })
    assert result["cpa"] is None
    assert result["recommendation"] in ("Reduce", "Pause", "Improve")


def test_high_ctr_but_bad_roas_must_not_recommend_keep_or_increase_budget():
    result = run({
        "impressions": 10000, "clicks": 600, "spend": 1000,
        "conversions": 20, "revenue": 400,
    })
    assert result["ctr"] == 6.0
    assert result["roas"] == 0.4
    assert result["recommendation"] in ("Reduce", "Pause")
    assert "ROAS" in result["rule_triggered"]


def test_exact_interview_stress_case_is_paused():
    result = run({
        "impressions": 10000, "clicks": 600, "spend": 1000,
        "conversions": 10, "revenue": 400,
    })
    assert result["ctr"] == 6.0
    assert round(result["cpc"], 2) == 1.67
    assert round(result["conversion_rate"], 2) == 1.67
    assert result["cpa"] == 100.0
    assert result["roas"] == 0.4
    assert result["recommendation"] == "Pause"


def test_high_roas_but_low_conversion_does_not_scale_automatically():
    result = run({
        "impressions": 100000, "clicks": 10000, "spend": 1000,
        "conversions": 100, "revenue": 5000,
    })
    assert result["roas"] == 5.0
    assert result["conversion_rate"] == 1.0
    assert result["recommendation"] == "Keep"
    assert "improve conversion before scaling" in result["rule_triggered"]
