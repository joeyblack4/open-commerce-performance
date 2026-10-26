"""Reversible preview projections. Never changes the served registry or merchant authority."""

from copy import copy

PREVIEW_STATES = ("shared", "withdrawn", "disputed")


def merchant_preview(registry, state, now):
    if state not in PREVIEW_STATES:
        raise ValueError("unknown preview state")
    simulation = copy(registry)
    simulation.consent = dict(registry.consent)
    simulation.lifecycle = {k: dict(v) for k, v in registry.lifecycle.items()}
    if state == "withdrawn":
        simulation.withdraw("fixture-a")
    elif state == "disputed":
        for identity, (tenant, _) in simulation.ownership.items():
            if tenant == "fixture-a":
                simulation.lifecycle[identity]["state"] = "disputed"
    subject = next(x for x in simulation.bundle(now)["merchants"] if x["subject"] == "fictional:merchant-a")
    return {
        "preview_only": True,
        "state": state,
        "merchant": subject,
        "live_registry_changed": False,
        "message": "Private simulation. No merchant connection, publication or consent record is changed.",
        "status_checks": [
            simulation.verification(i, now)
            for i, (tenant, _) in simulation.ownership.items()
            if tenant == "fixture-a"
        ],
        "categories": [
            {"id": "fulfilled_on_time_rate", "publication": state, "scope": "merchant delivery operations"},
            {"id": "order_complete_rate", "publication": state, "scope": "recorded fulfillment"},
            {"id": "order_refund_incidence", "publication": state, "scope": "settled refunds, with policy"},
            {
                "id": "voluntary_repeat",
                "publication": "unsupported",
                "scope": "no customer identity collected",
            },
            {
                "id": "product_reliability",
                "publication": "unsupported",
                "scope": "needs separate manufacturer evidence",
            },
        ],
    }
