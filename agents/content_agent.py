"""
Content Module — creates channel-specific draft content from the marketing
brief and Research Module output.

The running demo is deterministic and local. Claude Code assisted development,
but the app itself makes no external AI/API calls.
"""


def _specific_cta(brief: dict) -> str:
    product = brief["product"].strip()
    business = brief["business_name"].strip()
    objective = brief["objective"].strip().lower()

    if "sign" in objective or "book" in objective or "class" in product.lower():
        return f"Book your {product.lower()} with {business}."
    if "enquir" in objective or "lead" in objective or "contact" in objective:
        return f"Contact {business} about {product.lower()} today."
    if "sale" in objective or "purchase" in objective or "buy" in objective:
        return f"Explore {product.lower()} from {business} and choose the option that suits you."
    return f"See how {business}'s {product.lower()} can help with {brief['objective'].lower()}."


def run(brief: dict, research: dict) -> dict:
    channel = brief["channel"]
    business = brief["business_name"].strip()
    product = brief["product"].strip()
    audience = brief["audience"].strip()
    objective = brief["objective"].strip()
    tone = brief["tone"].strip()
    angle = research["campaign_angles"][0]
    cta = _specific_cta(brief)

    if channel == "Instagram":
        result = {
            "hook": f"Looking for a simpler way to get started with {product.lower()}?",
            "caption": (
                f"{business} offers {product.lower()} for {audience.lower()}. "
                f"This draft uses an outcome-led angle around {objective.lower()} while keeping the tone {tone.lower()}."
            ),
            "cta": cta,
            "video_idea": f"A short before/after or walkthrough showing what a first experience with {product.lower()} looks like.",
        }
    elif channel == "Google Search":
        result = {
            "headlines": [
                f"{product} | {business}",
                f"{objective} with {business}",
                f"{product} for {audience}",
            ],
            "descriptions": [
                f"Explore {product.lower()} from {business}, designed for {audience.lower()}.",
                f"Clear next steps and a {tone.lower()} experience focused on {objective.lower()}.",
            ],
            "keyword_ideas": [product, brief["industry"], objective],
            "landing_page_message": f"{product} for {audience}, with a clear path to {objective.lower()}.",
            "cta": cta,
        }
    elif channel == "Email":
        result = {
            "subject": f"A simple next step for {product.lower()}",
            "preview_text": f"How {business} can help with {objective.lower()}.",
            "email_body": (
                f"Hi,\n\nIf you're considering {product.lower()}, {business} has an option designed for {audience.lower()}. "
                f"The message focuses on {objective.lower()} and keeps the tone {tone.lower()}.\n\n{cta}"
            ),
            "cta": cta,
        }
    else:  # Website
        result = {
            "hero_headline": f"{product} built around your next step",
            "supporting_copy": (
                f"{business} helps {audience.lower()} move toward {objective.lower()} with a clear, {tone.lower()} experience."
            ),
            "cta": cta,
            "faq_ideas": [
                f"What is included with {product.lower()}?",
                f"Who is {product.lower()} best suited to?",
                f"What is the next step with {business}?",
            ],
        }

    result["_source"] = "local_deterministic"
    result["_campaign_angle_used"] = angle
    return result
