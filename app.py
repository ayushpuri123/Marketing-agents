"""Marketing Multi-Agent Assistant — local Streamlit portfolio prototype."""

import streamlit as st

from agents.analytics_agent import run as run_analytics
from agents.research_agent import run as run_research
from agents.content_agent import run as run_content
from agents.review_agent import run as run_review
from sample_data import SAMPLE_CAMPAIGNS

CHANNELS = ["Instagram", "Google Search", "Email", "Website"]
BUDGET_LEVELS = ["Low", "Medium", "High"]

st.set_page_config(page_title="Marketing Multi-Agent Assistant", layout="wide")


def render_kpis(result: dict):
    cols = st.columns(5)
    kpi_labels = [
        ("ctr", "CTR", "%"),
        ("cpc", "CPC", "$"),
        ("conversion_rate", "Conversion Rate", "%"),
        ("cpa", "CPA", "$"),
        ("roas", "ROAS", "x"),
    ]
    for col, (key, label, unit) in zip(cols, kpi_labels):
        value = result[key]
        if value is None:
            col.metric(label, "N/A")
        elif unit == "%":
            col.metric(label, f"{value:.1f}%")
        elif unit == "$":
            col.metric(label, f"${value:.2f}")
        else:
            col.metric(label, f"{value:.2f}x")


def render_recommendation(result: dict):
    recommendation = result["recommendation"]
    color_map = {
        "Keep": "green",
        "Test": "blue",
        "Improve": "orange",
        "Reduce": "orange",
        "Pause": "red",
        "Insufficient Data": "gray",
    }
    color = color_map.get(recommendation, "gray")
    st.markdown(f"### Recommendation: :{color}[{recommendation}]")
    st.write(result["reason"])
    st.info(f"**Rule triggered:** {result['rule_triggered']}")


def campaign_analysis_page():
    st.title("Campaign Analysis")
    st.caption(
        "Fully local and deterministic: KPI calculations and commercial rules are plain Python. "
        "No external AI/API calls are made."
    )

    data_source = st.radio(
        "Choose data source",
        ["Use sample campaign", "Enter data manually"],
        horizontal=True,
    )

    if data_source == "Use sample campaign":
        campaign_name = st.selectbox("Sample campaign", list(SAMPLE_CAMPAIGNS.keys()))
        metrics_input = SAMPLE_CAMPAIGNS[campaign_name]
        st.write("Raw data:", metrics_input)
    else:
        col1, col2 = st.columns(2)
        with col1:
            impressions = st.number_input("Impressions", min_value=0, value=1000, step=100)
            clicks = st.number_input("Clicks", min_value=0, value=50, step=10)
            spend = st.number_input("Spend ($)", min_value=0.0, value=100.0, step=10.0)
        with col2:
            conversions = st.number_input("Conversions", min_value=0, value=5, step=1)
            revenue = st.number_input("Revenue ($)", min_value=0.0, value=200.0, step=10.0)
        metrics_input = {
            "impressions": impressions,
            "clicks": clicks,
            "spend": spend,
            "conversions": conversions,
            "revenue": revenue,
        }

    if st.button("Analyse Campaign", type="primary"):
        result = run_analytics(metrics_input)
        review = run_review(
            {
                "business_name": "Campaign Analysis",
                "product": "campaign",
                "channel": "Website",
                "tone": "Professional",
            },
            analytics=result,
        )
        st.divider()
        render_kpis(result)
        st.divider()
        render_recommendation(result)
        with st.expander("Independent rule check", expanded=False):
            render_review_output(review)


def _local_logic_badge():
    st.caption("🧩 Local deterministic module — no external AI/API call")


def render_research_output(research: dict):
    _local_logic_badge()
    st.markdown(f"**Primary audience:** {research['primary_audience']}")
    st.markdown("**Likely pain points / needs (inferred):**")
    for point in research["pain_points"]:
        st.markdown(f"- {point}")
    st.markdown(f"**Likely customer intent:** {research['customer_intent']}")
    st.markdown("**Campaign angles:**")
    for angle in research["campaign_angles"]:
        st.markdown(f"- {angle}")
    st.markdown(f"**Keywords/themes:** {', '.join(research['keywords'])}")
    st.markdown("**Assumptions / evidence limits:**")
    for assumption in research["assumptions"]:
        st.markdown(f"- ⚠️ {assumption}")


def render_content_output(content: dict):
    _local_logic_badge()
    for key, value in content.items():
        if key.startswith("_"):
            continue
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            st.markdown(f"**{label}:**")
            for item in value:
                st.markdown(f"- {item}")
        else:
            st.markdown(f"**{label}:** {value}")


def render_review_output(review: dict):
    color_map = {"Pass": "green", "Needs Review": "orange", "Problem Found": "red"}
    color = color_map.get(review["status"], "gray")
    st.markdown(f"### Review: :{color}[{review['status']}] ")
    for finding in review["findings"]:
        st.write(f"- {finding}")


def marketing_brief_page():
    st.title("Marketing Brief")
    st.caption(
        "AI-assisted development, local execution: Claude Code helped build and iterate this prototype. "
        "The running workflow is deterministic so every output can be traced and tested without a paid API."
    )

    with st.form("brief_form"):
        col1, col2 = st.columns(2)
        with col1:
            business_name = st.text_input("Business name", "Riverside Yoga Studio")
            industry = st.text_input("Industry", "Fitness")
            product = st.text_input("Product/service", "Beginner yoga classes")
            audience = st.text_input("Target audience", "Busy professionals aged 25-40")
        with col2:
            objective = st.text_input("Marketing objective", "Increase new class sign-ups")
            channel = st.selectbox("Channel", CHANNELS)
            tone = st.text_input("Brand tone", "Calm and encouraging")
            budget_level = st.selectbox("Budget level", BUDGET_LEVELS)

        notes = st.text_area("Additional notes / restrictions", "")
        submitted = st.form_submit_button("Run Workflow", type="primary")

    if submitted:
        brief = {
            "business_name": business_name,
            "industry": industry,
            "product": product,
            "audience": audience,
            "objective": objective,
            "channel": channel,
            "tone": tone,
            "budget_level": budget_level,
            "notes": notes,
        }
        research = run_research(brief)
        content = run_content(brief, research)
        review = run_review(brief, research=research, content=content, analytics=None)

        st.session_state["brief_result"] = {
            "brief": brief,
            "research": research,
            "content": content,
            "review": review,
        }

    result = st.session_state.get("brief_result")
    if result:
        st.divider()
        st.markdown("**Workflow:** Brief → Research Module → Content Module → Review Module → Human decision")
        with st.expander("1. Research Module output", expanded=True):
            render_research_output(result["research"])
        with st.expander(f"2. Content Module output ({result['brief']['channel']})", expanded=False):
            render_content_output(result["content"])
        st.divider()
        render_review_output(result["review"])


def about_page():
    st.title("About This Project")

    st.header("The Problem")
    st.write(
        "Small businesses often move between audience thinking, content drafting, campaign analysis and quality review "
        "as separate tasks. This project demonstrates how those steps can be structured into a simple, traceable workflow."
    )

    st.header("What 'AI-assisted' Means Here")
    st.write(
        "Claude Code was used during development to help generate and iterate parts of the Python/Streamlit implementation. "
        "The running app itself is deliberately local and deterministic: it does not call Claude, OpenAI or any paid API. "
        "That makes the demo reproducible and lets the important rules be inspected and tested."
    )

    st.header("Architecture")
    st.code(
        "Marketing Brief\n"
        "  -> Research Module   (local deterministic brief interpretation)\n"
        "  -> Content Module    (local deterministic channel draft)\n"
        "  -> Review Module     (rule-based quality checks)\n"
        "  -> Human decision\n\n"
        "Campaign Analysis\n"
        "  -> KPI calculations  (pure Python)\n"
        "  -> Analytics Module  (transparent commercial rules)\n"
        "  -> Independent rule check",
        language="text",
    )

    st.header("Design Choices")
    st.markdown("""
- **Research Module:** only uses information supplied in the brief and labels inferred needs/intent as assumptions; it does not pretend to have external market research.
- **Content Module:** produces channel-specific draft content from the brief and research structure.
- **Analytics Module:** calculates CTR, CPC, conversion rate, CPA and ROAS in Python, then applies an explicit rule table. The exact rule that fired is shown in the UI.
- **Review Module:** checks unsupported claims, vague CTAs, channel completeness, brief drift, tone heuristics and recommendation consistency.
- **Human control:** every output is a draft or first-pass check, not an autonomous publishing or budget decision.
""")

    st.header("Testing")
    st.write(
        "The deterministic logic is covered by pytest tests, including divide-by-zero handling, profitable and losing campaigns, "
        "the high-CTR/low-ROAS edge case, unsupported claims and recommendation consistency."
    )
    st.code("pytest tests/ -v", language="bash")

    st.header("A Real Claude Code Logic Bug")
    st.write(
        "During AI-assisted development, an early recommendation function checked CTR before ROAS. "
        "That meant a high-click campaign with ROAS 0.4 could incorrectly receive a positive recommendation. "
        "A regression test exposed the issue; the logic was changed so profitability is checked first. "
        "The original failure and fix are documented in FAILURE_LOG.md."
    )

    st.header("Limitations")
    st.markdown("""
- Research outputs are structured inferences from the user's brief, not real market research.
- Content is deterministic template logic, so it is less flexible than a live LLM.
- Review checks are heuristics and can miss nuanced problems or raise false positives.
- ROAS thresholds are demonstration rules, not universal commercial benchmarks; a real business would configure them around margins and objectives.
- No persistence or production integrations are included.
""")

    st.header("Possible Production Extension")
    st.write(
        "A future version could connect the Research, Content and softer Review tasks to an LLM while keeping KPI calculations, "
        "profitability guardrails and regression tests deterministic."
    )


PAGES = {
    "Marketing Brief": marketing_brief_page,
    "Campaign Analysis": campaign_analysis_page,
    "About Project": about_page,
}


def main():
    st.sidebar.title("Marketing Multi-Agent Assistant")
    st.sidebar.caption("AI-assisted development • local deterministic demo")
    choice = st.sidebar.radio("Navigate", list(PAGES.keys()), index=0)
    PAGES[choice]()


if __name__ == "__main__":
    main()
