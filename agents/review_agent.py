"""
Review Module — deterministic first-pass quality checks over the workflow.

This is intentionally a rules-based safety/quality layer, not a claim that the
app can replace human marketing judgement.
"""

from utils.validation import (
    find_unsupported_claims,
    is_vague_cta,
    check_recommendation_consistency,
    mentions_business_context,
    has_excessive_punctuation,
    missing_channel_fields,
)

CALM_TONE_KEYWORDS = {"calm", "professional", "formal", "trustworthy", "reassuring"}


def _collect_text_fields(data: dict) -> list[str]:
    texts = []
    for key, value in data.items():
        if key.startswith("_"):
            continue
        if isinstance(value, str):
            texts.append(value)
        elif isinstance(value, list):
            texts.extend(v for v in value if isinstance(v, str))
    return texts


def run(brief: dict, research: dict = None, content: dict = None, analytics: dict = None) -> dict:
    findings = []
    has_problem = False
    needs_review = False

    all_texts = []
    if research:
        all_texts.extend(_collect_text_fields(research))
    if content:
        all_texts.extend(_collect_text_fields(content))

    claims = []
    for text in all_texts:
        claims.extend(find_unsupported_claims(text))
    if claims:
        has_problem = True
        findings.append(
            f"Unsupported claim(s) detected: {sorted(set(claims))}. Verify or remove them before publishing."
        )

    if analytics:
        consistency = check_recommendation_consistency(analytics, analytics.get("recommendation"))
        if not consistency["consistent"]:
            has_problem = True
            findings.append(
                f"Recommendation inconsistency: '{analytics.get('recommendation')}' does not match the deterministic rule table; expected '{consistency['expected']}'."
            )

    if content:
        missing = missing_channel_fields(content, brief["channel"])
        if missing:
            has_problem = True
            findings.append(
                f"Channel mismatch/incomplete output for {brief['channel']}: missing {', '.join(missing)}."
            )

        for key, value in content.items():
            if "cta" in key.lower() and isinstance(value, str) and is_vague_cta(value):
                needs_review = True
                findings.append(f"Vague CTA detected in '{key}': '{value}'. Make it specific to the offer or next step.")

        combined = " ".join(_collect_text_fields(content))
        if not mentions_business_context(combined, brief["business_name"], brief["product"]):
            needs_review = True
            findings.append("Content does not mention the business or product/service and may be drifting from the brief.")

        tone_lower = brief.get("tone", "").lower()
        if any(keyword in tone_lower for keyword in CALM_TONE_KEYWORDS) and has_excessive_punctuation(combined):
            needs_review = True
            findings.append(
                f"Brand tone is '{brief['tone']}' but the content uses excessive exclamation marks, which may feel too hype-heavy."
            )

    if has_problem:
        status = "Problem Found"
    elif needs_review:
        status = "Needs Review"
    else:
        status = "Pass"
        findings.append("No issues detected by the automated first-pass checks.")

    return {"status": status, "findings": findings}
