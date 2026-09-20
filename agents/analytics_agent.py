"""
Analytics Module — deterministic campaign calculations and recommendations.

No LLM is used. Profitability is checked before engagement metrics, and the
exact human-readable rule that fired is returned with every recommendation.
"""

from utils.metrics import CampaignMetrics, calculate_all_metrics

ROAS_PAUSE_THRESHOLD = 0.5
ROAS_REDUCE_THRESHOLD = 1.0
ROAS_KEEP_THRESHOLD = 2.0
ROAS_TEST_THRESHOLD = 4.0
TEST_CONVERSION_THRESHOLD = 3.0

CTR_HIGH_THRESHOLD = 5.0
CTR_LOW_THRESHOLD = 1.0
CONVERSION_LOW_THRESHOLD = 1.0


def _primary_recommendation(roas: float, conversion_rate: float | None = None) -> tuple[str, str, str]:
    if roas < ROAS_PAUSE_THRESHOLD:
        return (
            "Pause",
            f"ROAS is {roas:.2f} — the campaign is returning less than half of ad spend.",
            f"ROAS < {ROAS_PAUSE_THRESHOLD:.1f} -> Pause",
        )
    if roas < ROAS_REDUCE_THRESHOLD:
        return (
            "Reduce",
            f"ROAS is {roas:.2f}, below break-even (1.0). The campaign is losing money.",
            f"{ROAS_PAUSE_THRESHOLD:.1f} <= ROAS < {ROAS_REDUCE_THRESHOLD:.1f} -> Reduce",
        )
    if roas < ROAS_KEEP_THRESHOLD:
        return (
            "Improve",
            f"ROAS is {roas:.2f} — positive revenue, but not strong enough to scale confidently.",
            f"{ROAS_REDUCE_THRESHOLD:.1f} <= ROAS < {ROAS_KEEP_THRESHOLD:.1f} -> Improve",
        )
    if roas < ROAS_TEST_THRESHOLD:
        return (
            "Keep",
            f"ROAS is {roas:.2f} — commercially healthy enough to keep running while monitoring quality.",
            f"{ROAS_KEEP_THRESHOLD:.1f} <= ROAS < {ROAS_TEST_THRESHOLD:.1f} -> Keep",
        )

    if conversion_rate is not None and conversion_rate >= TEST_CONVERSION_THRESHOLD:
        return (
            "Test",
            f"ROAS is {roas:.2f} and conversion rate is {conversion_rate:.1f}% — strong enough to test a controlled budget increase.",
            f"ROAS >= {ROAS_TEST_THRESHOLD:.1f} AND conversion rate >= {TEST_CONVERSION_THRESHOLD:.1f}% -> Test controlled budget increase",
        )

    return (
        "Keep",
        f"ROAS is {roas:.2f}, but conversion rate is {conversion_rate:.1f}% — keep the campaign stable and improve conversion before testing more budget.",
        f"ROAS >= {ROAS_TEST_THRESHOLD:.1f} BUT conversion rate < {TEST_CONVERSION_THRESHOLD:.1f}% -> Keep and improve conversion before scaling",
    )


def _diagnostic_note(ctr: float | None, conversion_rate: float | None) -> str:
    if ctr is not None and ctr >= CTR_HIGH_THRESHOLD and conversion_rate is not None and conversion_rate < CONVERSION_LOW_THRESHOLD:
        return (
            f" Note: CTR is high ({ctr:.1f}%) but conversion rate is low ({conversion_rate:.1f}%) — "
            "investigate the landing page, offer or traffic quality before changing creative."
        )
    if ctr is not None and ctr < CTR_LOW_THRESHOLD:
        return f" Note: CTR is low ({ctr:.1f}%) — investigate targeting, message or creative."
    return ""


def generate_recommendation(kpis: dict) -> dict:
    ctr = kpis["ctr"]
    conversion_rate = kpis["conversion_rate"]
    roas = kpis["roas"]

    if roas is None:
        return {
            "recommendation": "Insufficient Data",
            "reason": "ROAS could not be calculated because no spend was recorded.",
            "rule_triggered": "Spend = 0 -> ROAS unavailable -> Insufficient Data",
        }

    recommendation, reason, rule_triggered = _primary_recommendation(roas, conversion_rate)
    reason += _diagnostic_note(ctr, conversion_rate)
    return {
        "recommendation": recommendation,
        "reason": reason,
        "rule_triggered": rule_triggered,
    }


def run(metrics_input: dict) -> dict:
    metrics = CampaignMetrics(**metrics_input)
    kpis = calculate_all_metrics(metrics)
    rec = generate_recommendation(kpis)
    return {**kpis, **rec}
