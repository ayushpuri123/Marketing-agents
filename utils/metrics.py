"""
Deterministic marketing KPI calculations.

DETERMINISTIC — no LLM, no randomness. Every function here is pure Python
arithmetic and is fully covered by tests in tests/test_metrics.py.

Design choice: when a calculation is mathematically undefined (e.g. dividing
by zero impressions), we return None rather than 0.0. Returning 0.0 would be
misleading — a CTR of 0.0 normally means "clicks happened, conversion just
didn't" which is a real, meaningful result. It should not be confused with
"we have no data to calculate this at all." Callers (agents/UI) are expected
to handle None explicitly and show something like "N/A" rather than a
misleading number.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CampaignMetrics:
    """Raw inputs needed to calculate all KPIs."""
    impressions: int
    clicks: int
    spend: float
    conversions: int
    revenue: float


def calculate_ctr(clicks: int, impressions: int) -> Optional[float]:
    """Click-through rate, as a percentage. clicks / impressions * 100."""
    if impressions == 0:
        return None
    return (clicks / impressions) * 100


def calculate_cpc(spend: float, clicks: int) -> Optional[float]:
    """Cost per click. spend / clicks."""
    if clicks == 0:
        return None
    return spend / clicks


def calculate_conversion_rate(conversions: int, clicks: int) -> Optional[float]:
    """Conversion rate, as a percentage. conversions / clicks * 100."""
    if clicks == 0:
        return None
    return (conversions / clicks) * 100


def calculate_cpa(spend: float, conversions: int) -> Optional[float]:
    """Cost per acquisition. spend / conversions."""
    if conversions == 0:
        return None
    return spend / conversions


def calculate_roas(revenue: float, spend: float) -> Optional[float]:
    """Return on ad spend. revenue / spend. A value of 1.0 means break-even."""
    if spend == 0:
        return None
    return revenue / spend


def calculate_all_metrics(metrics: CampaignMetrics) -> dict:
    """
    Run every KPI calculation on one CampaignMetrics input and return a
    single dict. This is the function agents/analytics_agent.py calls.
    """
    return {
        "ctr": calculate_ctr(metrics.clicks, metrics.impressions),
        "cpc": calculate_cpc(metrics.spend, metrics.clicks),
        "conversion_rate": calculate_conversion_rate(metrics.conversions, metrics.clicks),
        "cpa": calculate_cpa(metrics.spend, metrics.conversions),
        "roas": calculate_roas(metrics.revenue, metrics.spend),
    }
