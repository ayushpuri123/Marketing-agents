"""Deterministic validation helpers for the Review Module."""

import re
from agents.analytics_agent import _primary_recommendation

UNSUPPORTED_CLAIM_PATTERNS = [
    r"\bstudies show\b",
    r"\bclinically proven\b",
    r"\bscientifically proven\b",
    r"\bguaranteed\b",
    r"\b#1\b",
    r"\bbest in the (world|industry|country)\b",
    r"\b\d{1,3}%\s+of\s+(customers|people|users|clients)\b",
    r"\baward[- ]winning\b",
    r"\bindustry leader\b",
]

VAGUE_CTA_PHRASES = {"click here", "learn more", "get started", "sign up", "buy now", "shop now"}

CHANNEL_REQUIRED_KEYS = {
    "Instagram": {"hook", "caption", "cta", "video_idea"},
    "Google Search": {"headlines", "descriptions", "keyword_ideas", "landing_page_message", "cta"},
    "Email": {"subject", "preview_text", "email_body", "cta"},
    "Website": {"hero_headline", "supporting_copy", "cta", "faq_ideas"},
}


def find_unsupported_claims(text: str) -> list[str]:
    if not text:
        return []
    lowered = text.lower()
    matches = []
    for pattern in UNSUPPORTED_CLAIM_PATTERNS:
        for match in re.finditer(pattern, lowered):
            matches.append(match.group(0))
    return matches


def is_vague_cta(cta: str) -> bool:
    if not cta:
        return True
    stripped = cta.strip().lower().rstrip(".!")
    return stripped in VAGUE_CTA_PHRASES


def check_recommendation_consistency(kpis: dict, stated_recommendation: str) -> dict:
    roas = kpis.get("roas")
    conversion_rate = kpis.get("conversion_rate")
    if roas is None:
        return {"consistent": stated_recommendation == "Insufficient Data", "expected": "Insufficient Data"}

    expected_recommendation, _, _ = _primary_recommendation(roas, conversion_rate)
    return {
        "consistent": expected_recommendation == stated_recommendation,
        "expected": expected_recommendation,
    }


def mentions_business_context(text: str, business_name: str, product: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return business_name.lower() in lowered or product.lower() in lowered


def has_excessive_punctuation(text: str, threshold: int = 2) -> bool:
    if not text:
        return False
    return text.count("!") >= threshold


def missing_channel_fields(content: dict, channel: str) -> list[str]:
    required = CHANNEL_REQUIRED_KEYS.get(channel, set())
    return sorted(key for key in required if key not in content or not content.get(key))
