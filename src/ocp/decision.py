"""Transparent shopper-specific policy demonstration, not an LLM or universal ranking."""

from .metrics import compare

OFFERS = [
    {
        "subject": "fictional:merchant-a",
        "price": 24,
        "available": True,
        "item": "fixture-identical-grocery-box",
    },
    {
        "subject": "fictional:merchant-b",
        "price": 20,
        "available": True,
        "item": "fixture-identical-grocery-box",
    },
    {
        "subject": "fictional:merchant-unknown",
        "price": 18,
        "available": True,
        "item": "fixture-identical-grocery-box",
    },
]
SCENARIOS = {
    "delivery": {"label": "Delivery matters · up to $25", "max_price": 25, "min_historical_on_time": 0.85},
    "price": {"label": "Lowest price · up to $21", "max_price": 21, "min_historical_on_time": None},
    "tight": {"label": "Delivery matters · under $20", "max_price": 19, "min_historical_on_time": 0.85},
}


def decide(bundle, scenario, use_evidence=True):
    if scenario not in SCENARIOS:
        raise ValueError("unknown scenario")
    preference = SCENARIOS[scenario]
    merchants = {m["subject"]: m for m in bundle["merchants"]}
    assessments = []
    candidates = []
    for offer in OFFERS:
        subject = offer["subject"]
        within = offer["available"] and offer["price"] <= preference["max_price"]
        evidence = next(
            (
                x
                for x in merchants.get(subject, {}).get("evidence", [])
                if x["statement"]["metric"]["id"] == "fulfilled_on_time_rate"
            ),
            None,
        )
        statement = evidence["statement"] if evidence else None
        valid = bool(
            use_evidence
            and evidence
            and evidence["verification"]["current"]
            and evidence["verification"]["signature_valid"]
            and evidence["verification"]["arithmetic_consistent"]
            and evidence["verification"]["usable_as_synthetic_evidence"]
            and statement["metric"]["status"] == "observed"
        )
        rate = statement["metric"]["value"] if valid else None
        required = preference["min_historical_on_time"]
        satisfies = required is None or rate is not None and rate >= required
        reason = (
            "outside price/availability constraints"
            if not within
            else "price preference; delivery history remains a separate tradeoff"
            if required is None
            else "insufficient current evidence; unknown is not poor performance"
            if rate is None
            else "observed historical cohort meets your threshold; no delivery guarantee"
            if satisfies
            else "observed historical cohort falls below your threshold"
        )
        assessments.append(
            {
                **offer,
                "eligible": within,
                "historical_on_time": rate,
                "reason": reason,
                "statement_id": statement["statement_id"] if valid else None,
            }
        )
        if within and satisfies:
            candidates.append((offer, statement))
    # Compare scope/policy before choosing among multiple qualifying evidence-bearing offers.
    if preference["min_historical_on_time"] is not None and len(candidates) > 1:
        anchor = candidates[0][1]
        if any(not compare(anchor, candidate[1])["comparable"] for candidate in candidates[1:]):
            return {
                "scenario": scenario,
                "choice": None,
                "state": "not_comparable",
                "assessments": assessments,
                "reason": "Relevant cohorts differ; no forced winner.",
            }
    choice = min(candidates, key=lambda pair: pair[0]["price"])[0]["subject"] if candidates else None
    return {
        "scenario": scenario,
        "choice": choice,
        "state": "selected" if choice else "insufficient_evidence",
        "assessments": assessments,
        "reason": (
            "Lowest priced eligible offer meeting your stated evidence preference."
            if choice
            else "No eligible offer has sufficient evidence for your delivery preference. Consider a higher budget "
            "or ask for more evidence; no merchant is labelled unreliable because it did not publish."
        ),
        "limitations": "Deterministic policy on fictional offers and synthetic history. Not an LLM test, "
        "a forecast, a product-quality claim or real consumer validation.",
    }
