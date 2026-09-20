# AI Failure Log — Marketing Multi-Agent Assistant

This file documents a real mistake Claude made during development, exactly as it
happened, so it can be discussed honestly (e.g. in an interview) rather than
hidden. This was not staged — it's the actual first version of the code and the
actual test failure.

---

## Failure: CTR checked before ROAS in the Analytics Agent's recommendation logic

### 1. What Claude generated

The first version of `agents/analytics_agent.py::generate_recommendation()`
checked CTR before ROAS:

```python
if ctr is not None and ctr >= CTR_HIGH_THRESHOLD:
    if conversion_rate is not None and conversion_rate < CONVERSION_LOW_THRESHOLD:
        return {"recommendation": "Improve", ...}
    return {"recommendation": "Keep", "reason": f"CTR is strong ({ctr:.1f}%)..."}

if roas is not None and roas < 1.0:
    return {"recommendation": "Reduce", ...}
```

### 2. Why it is wrong

The project brief explicitly requires: **"The system must NOT recommend
increasing budget just because CTR is high. Profitability/ROAS must be
considered first."**

The code above does the opposite. It was written by translating the brief's
bullet list of example principles into `if/elif` branches in roughly the
order they appeared in the prompt, rather than ordering them by business
priority. As a result:

- Input: CTR = 6% (high), ROAS = 0.4 (losing 60 cents per dollar spent),
  conversion rate = 3.3% (not "low" by the 1% threshold).
- The CTR branch matched first and returned early with **"Keep"** and the
  reason *"CTR is strong (6.0%), campaign is engaging the audience well."*
- The ROAS check was never reached. A campaign that is actively losing money
  was recommended to keep running, based only on a vanity metric (CTR).

This is a **logic ordering bug**, not a typo or crash — the code ran fine and
produced a confident, plausible-sounding, wrong answer. That's what makes it
worth documenting: it wouldn't have been caught by reading the code casually.

### 3. How it was detected

A test written specifically for this scenario:

```python
def test_high_ctr_but_bad_roas_must_not_recommend_keep_or_increase_budget():
    result = run({
        "impressions": 10000, "clicks": 600, "spend": 1000,
        "conversions": 20, "revenue": 400,
    })
    assert result["recommendation"] in ("Reduce", "Pause")
```

Running `pytest tests/test_analytics_agent.py -v` failed with:

```
AssertionError: Expected Reduce/Pause for a losing campaign, got 'Keep' —
high CTR incorrectly overrode poor ROAS.
```

Without this test, the bug would likely have shipped — it only manifests
when CTR is high AND ROAS is bad AND conversion rate isn't low enough to
trip the inner check. Manually clicking through the sample data would catch
it if you happened to check the `high_ctr_bad_roas` sample and knew to
distrust a "Keep" verdict — but a test makes it impossible to miss.

### 4. How it was fixed

Rewrote `generate_recommendation()` so that **ROAS decides the primary
recommendation first, unconditionally**, via `_primary_recommendation()`:

```python
ROAS_PAUSE_THRESHOLD = 0.5
ROAS_REDUCE_THRESHOLD = 1.0
ROAS_KEEP_THRESHOLD = 2.0
ROAS_TEST_THRESHOLD = 4.0
```

CTR can no longer override the profitability decision. Conversion rate is used only as a secondary scaling guardrail after ROAS is already strong: a campaign with high ROAS but weak conversion is kept stable rather than automatically recommended for a budget-increase test.

### 5. Test added

`tests/test_analytics_agent.py::test_high_ctr_but_bad_roas_must_not_recommend_keep_or_increase_budget`
— kept permanently in the suite as a regression guard. It uses the exact
scenario from the project brief (CTR 6%, ROAS 0.4) and asserts the
recommendation must be Reduce or Pause.

---

## Takeaway for discussion

This is a good example of a subtle but real risk with AI-assisted coding:
the generated code was syntactically correct, ran without errors, and
matched the individual bullet points in the spec — but the *order* in which
those rules were applied inverted the intended business logic. It was only
caught because a specific, business-critical test case was written before
trusting the code. This is also why the deterministic/rule-based parts of
this project are unit tested as rigorously as they are — correctness here
has real commercial consequences, unlike a wrong word choice in generated
ad copy.
