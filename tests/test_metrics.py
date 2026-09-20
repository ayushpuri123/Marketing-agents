"""
Tests for utils/metrics.py — the deterministic KPI calculations.

Run with: pytest tests/test_metrics.py -v
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.metrics import (
    CampaignMetrics,
    calculate_ctr,
    calculate_cpc,
    calculate_conversion_rate,
    calculate_cpa,
    calculate_roas,
    calculate_all_metrics,
)


# ---------- CTR ----------

def test_ctr_normal_case():
    assert calculate_ctr(clicks=50, impressions=1000) == 5.0


def test_ctr_zero_impressions_returns_none():
    assert calculate_ctr(clicks=0, impressions=0) is None


def test_ctr_zero_clicks_is_valid_zero_not_none():
    # Zero clicks with real impressions is a meaningful 0%, not "undefined".
    assert calculate_ctr(clicks=0, impressions=1000) == 0.0


# ---------- CPC ----------

def test_cpc_normal_case():
    assert calculate_cpc(spend=100, clicks=50) == 2.0


def test_cpc_zero_clicks_returns_none():
    assert calculate_cpc(spend=100, clicks=0) is None


# ---------- Conversion rate ----------

def test_conversion_rate_normal_case():
    assert calculate_conversion_rate(conversions=5, clicks=100) == 5.0


def test_conversion_rate_zero_clicks_returns_none():
    assert calculate_conversion_rate(conversions=0, clicks=0) is None


def test_conversion_rate_zero_conversions_is_valid_zero():
    assert calculate_conversion_rate(conversions=0, clicks=100) == 0.0


# ---------- CPA ----------

def test_cpa_normal_case():
    assert calculate_cpa(spend=500, conversions=10) == 50.0


def test_cpa_zero_conversions_returns_none():
    # This matters: spend happened but nothing converted. Undefined, not $0.
    assert calculate_cpa(spend=500, conversions=0) is None


# ---------- ROAS ----------

def test_roas_normal_case():
    assert calculate_roas(revenue=400, spend=200) == 2.0


def test_roas_zero_spend_returns_none():
    assert calculate_roas(revenue=400, spend=0) is None


def test_roas_below_one_means_losing_money():
    # revenue < spend => ROAS < 1.0, a losing campaign.
    result = calculate_roas(revenue=400, spend=1000)
    assert result == 0.4
    assert result < 1.0


# ---------- calculate_all_metrics / integration ----------

def test_calculate_all_metrics_normal_case():
    metrics = CampaignMetrics(
        impressions=10000, clicks=600, spend=1000, conversions=30, revenue=3000
    )
    result = calculate_all_metrics(metrics)
    assert result["ctr"] == 6.0
    assert round(result["cpc"], 2) == 1.67
    assert result["conversion_rate"] == 5.0
    assert round(result["cpa"], 2) == 33.33
    assert result["roas"] == 3.0


def test_calculate_all_metrics_all_zero_inputs():
    metrics = CampaignMetrics(impressions=0, clicks=0, spend=0, conversions=0, revenue=0)
    result = calculate_all_metrics(metrics)
    assert result == {
        "ctr": None,
        "cpc": None,
        "conversion_rate": None,
        "cpa": None,
        "roas": None,
    }


def test_high_ctr_bad_roas_stress_scenario():
    """
    This is the exact scenario from the project brief:
    CTR = 6%, spend = $1000, revenue = $400 => ROAS = 0.4

    The point of this test is NOT the math (that's covered above) — it's
    a marker test that documents this specific combination is the one the
    Analytics Agent's recommendation logic must handle correctly (see
    test_analytics_agent.py). High CTR must never be allowed to override
    poor ROAS in the final recommendation.
    """
    metrics = CampaignMetrics(
        impressions=10000, clicks=600, spend=1000, conversions=20, revenue=400
    )
    result = calculate_all_metrics(metrics)
    assert result["ctr"] == 6.0
    assert result["roas"] == 0.4
