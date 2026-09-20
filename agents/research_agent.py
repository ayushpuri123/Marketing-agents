"""
Research Module — turns a marketing brief into a structured direction.

This running demo is fully local and deterministic. Claude Code was used as
an AI development assistant while building and iterating the project, but the
app itself makes no external AI/API calls.

The module does not claim to perform external market research. It only
reframes information supplied in the brief and labels any inferred needs or
intent as assumptions.
"""


def run(brief: dict) -> dict:
    audience = brief["audience"].strip()
    product = brief["product"].strip()
    objective = brief["objective"].strip()
    tone = brief["tone"].strip()
    industry = brief["industry"].strip()
    channel = brief["channel"].strip()
    budget = brief["budget_level"].strip()
    notes = (brief.get("notes") or "").strip()

    pain_points = [
        f"May need a clear reason to choose {product} over doing nothing or delaying the decision.",
        f"May want the value and next step explained quickly before committing to {objective.lower()}.",
        f"May need reassurance that {product} fits their needs, schedule or budget.",
    ]

    campaign_angles = [
        f"Outcome-led: connect {product} directly to the goal of {objective.lower()}.",
        f"Audience-led: show how {product} fits the needs of {audience}.",
        f"Trust-led: use a {tone.lower()} tone to make the next step feel clear and low-friction.",
    ]

    keywords = [
        industry,
        product,
        objective,
        audience,
        channel,
    ]

    assumptions = [
        "ASSUMPTION: The likely needs and intent below are inferred from the brief, not from external customer research.",
        f"ASSUMPTION: A {budget.lower()} budget means the campaign should prioritise focused tests rather than broad reach.",
    ]
    if notes:
        assumptions.append(f"Brief restriction supplied by user: {notes}")
    else:
        assumptions.append("ASSUMPTION: No additional restrictions or market evidence were supplied.")

    return {
        "primary_audience": audience,
        "pain_points": pain_points,
        "customer_intent": (
            f"Likely evaluating whether {product} is relevant and worth acting on; "
            f"this is an assumption based only on the stated objective: {objective}."
        ),
        "campaign_angles": campaign_angles,
        "keywords": keywords,
        "assumptions": assumptions,
        "_source": "local_deterministic",
    }
