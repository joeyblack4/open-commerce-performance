"""Closed-world business-fit example; not a directory or a new UCP capability."""

from .decision import decide_with_preferences

CONTEXTS = {
    "shipped-order": "Standard shipped grocery order",
    "local-pickup": "Local pickup",
    "prepared-meal": "Prepared meal delivery",
}


def discover_businesses(bundle, context, preference, use_evidence=True):
    if context not in CONTEXTS:
        raise ValueError("unsupported discovery context")
    # Validate even when context cannot be supported; an unknown scope never widens policy.
    decision = decide_with_preferences(bundle, preference, use_evidence)
    in_scope = context == "shipped-order"
    return {
        "experimental": True,
        "synthetic": True,
        "context": context,
        "context_label": CONTEXTS[context],
        "candidate_source": "Three explicitly seeded fictional merchants; no web search or global index.",
        "market_coverage": "unknown",
        "entity_scope": "Merchant only; no brand, branch, franchise or product-quality inference.",
        "state": "assessed" if in_scope else "scope_not_established",
        "candidates": [
            {
                "subject": m["subject"],
                "name": m["name"],
                "service_fit": "fixture_offer_in_scope" if in_scope else "not_established",
            }
            for m in bundle["merchants"]
        ],
        "decision": decision if in_scope else None,
        "reason": (
            "Compare these seeded merchants for the same shipped order under the shopper's preferences."
            if in_scope
            else "The shipped-order fixture establishes neither service eligibility nor relevant outcomes "
            "for this need. No business recommendation can be justified from it, including on price."
        ),
        "limitations": "Shipped-offer fit is a fixed synthetic assumption, not verified serviceability. "
        "Candidate discovery is seeded; evidence verification cannot recover omitted businesses. "
        "No live UCP discovery, location lookup, global search or forecast is implemented.",
    }
