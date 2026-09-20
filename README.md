# Marketing Multi-Agent Assistant

A small Streamlit portfolio prototype that structures a basic marketing workflow into research, content, analytics and review stages.

## What the project demonstrates

This is an **AI-assisted development project**, not a live-LLM product.
Claude Code was used to help implement and iterate the Python/Streamlit app. The running demo is deliberately local and deterministic, so it works without paid APIs and its important rules can be inspected and tested.

The project focuses on a practical question: how can a small marketing workflow be made more structured, explainable and testable without handing important commercial decisions to a black box?

## Workflow

```text
Marketing Brief
  -> Research Module
  -> Content Module
  -> Review Module
  -> Human decision

Campaign Analysis
  -> KPI calculations
  -> Analytics Module
  -> Independent rule check
```

The folder and project name still use the original “agent” terminology, but each stage is intentionally just a small Python module/function rather than an autonomous agent framework.

## Modules

### Research Module
- Uses only information supplied in the marketing brief.
- Structures likely audience needs, intent, campaign angles and themes.
- Labels inferred information as assumptions.
- Does not claim external customer research, competitor facts or market statistics.

### Content Module
- Produces a deterministic channel-specific draft for Instagram, Google Search, Email or Website.
- Uses the original brief plus the selected campaign angle.
- Keeps the CTA tied to the product/business rather than generic “learn more” language.

### Analytics Module
Calculates these metrics in plain Python:
- CTR
- CPC
- Conversion rate
- CPA
- ROAS

It then applies a transparent recommendation table:
- Pause
- Reduce
- Improve
- Keep
- Test

The UI shows the exact human-readable rule that fired. Profitability is checked before engagement metrics. A strong ROAS must also meet a conversion-rate guardrail before the app recommends a controlled budget-increase test.

### Review Module
Performs deterministic first-pass checks for:
- Unsupported or invented claims
- Vague CTAs
- Missing channel-specific output fields
- Content drifting away from the original brief
- Simple tone mismatch signals
- Analytics recommendations inconsistent with the underlying KPI rule table

It returns:
- Pass
- Needs Review
- Problem Found

The Review Module is a first-pass gate only. A human remains responsible for the final decision.

## Project structure

```text
marketing_agents/
    app.py
    agents/
        research_agent.py
        content_agent.py
        analytics_agent.py
        review_agent.py
    utils/
        metrics.py
        validation.py
    tests/
        test_metrics.py
        test_analytics_agent.py
        test_review_agent.py
        test_workflow_modules.py
    sample_data.py
    requirements.txt
    README.md
    FAILURE_LOG.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

No API key is required.

## Run

```bash
streamlit run app.py
```

## Test

```bash
pytest tests/ -v
```

The tests cover KPI calculations, zero-denominator handling, recommendation rules, rule transparency, high-CTR/low-ROAS edge cases, unsupported claims, channel completeness and the deterministic Research/Content workflow.

## AI-assisted development approach

The ownership split is intentionally transparent:

- I defined the problem, workflow, module responsibilities, important commercial guardrails and test scenarios.
- Claude Code assisted with implementation and iteration.
- I ran and reviewed the generated code rather than treating “it runs” as proof that the logic is correct.
- I used tests and deliberately conflicting campaign metrics to challenge the recommendation logic.
- The running app is local/deterministic rather than using a paid LLM API.

A production extension could connect the Research, Content and softer Review tasks to an LLM while keeping KPI math, profitability guardrails and regression tests deterministic.

## Real AI-assisted coding failure

During development, an early version of the Analytics Module checked CTR before ROAS. A campaign with a 6% CTR but ROAS of 0.4 could therefore receive a positive “Keep” recommendation even though it was losing money.

The bug was caught with a regression test for the conflicting-metrics scenario. The logic was changed so profitability is evaluated first; CTR/conversion now provide diagnostics rather than overriding a losing ROAS.

See `FAILURE_LOG.md` for the original logic, the failed test and the correction.

## Limitations

- Research output is structured inference from the user-provided brief, not real market research.
- Content uses deterministic local logic and is less flexible than live generative AI.
- Review checks are heuristics and can miss nuanced issues or raise false positives.
- ROAS/conversion thresholds are demonstration rules, not universal business benchmarks; a real company would configure them around margin, LTV and campaign objectives.
- No persistence, authentication or production integrations are included.

## Why the project stays small

The goal is explainability. There is no agent orchestration framework, vector database, autonomous loop, CRM integration or unnecessary infrastructure. Each important decision can be traced to a small function, rule or test.
