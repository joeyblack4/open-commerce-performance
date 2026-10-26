"""Read-only fixture source, not Shopify API conformance. No HTTP/OAuth/customer fields."""

from dataclasses import replace
from ..model import Order, Snapshot, validate_snapshot

TENANTS = {
    "fixture-a": "fictional:merchant-a",
    "fixture-b": "fictional:merchant-b",
    "fixture-unknown": "fictional:merchant-unknown",
}


def read_snapshot(tenant: str) -> tuple[Snapshot, dict]:
    if tenant not in TENANTS:
        raise ValueError("unknown synthetic tenant")
    orders = []
    for i in range(1000):
        worse = tenant == "fixture-b"
        unknown = tenant == "fixture-unknown"
        late = i < (250 if worse else 100)
        incomplete = i < (200 if worse else 50)
        refund = i < (150 if worse else 50)
        orders.append(
            Order(
                tenant=tenant,
                order_id=f"synthetic-{i:04d}",
                purchased_at="2026-04-15T12:00:00Z",
                paid=True,
                test=False,
                cancelled=False,
                promise_at_checkout=None if unknown else "2026-04-20T12:00:00Z",
                promise_recorded_at=None if unknown else "2026-04-15T12:00:00Z",
                fulfilled_at="2026-04-17T12:00:00Z",
                delivered_at=None
                if unknown
                else ("2026-04-21T12:00:00Z" if late else "2026-04-19T12:00:00Z"),
                delivery_evidence="none" if unknown else "synthetic_carrier",
                committed=(("fixture-sku-1", 2),),
                fulfilled=None if unknown else (("fixture-sku-1", 1 if incomplete else 2),),
                delivered=None if unknown else (("fixture-sku-1", 1 if incomplete else 2),),
                refunds_settled_at=None if unknown else (("2026-05-01T00:00:00Z",) if refund else ()),
            )
        )
    snapshot = Snapshot(
        tenant,
        TENANTS[tenant],
        "2026-04-01T00:00:00Z",
        "2026-07-01T00:00:00Z",
        "2026-10-25T12:00:00Z",
        tuple(orders),
        1000,
        True,
    )
    validate_snapshot(snapshot)
    receipt = {
        "adapter": "shopify_mock/0.2.0",
        "access": "synthetic_read_only",
        "authentication": "not_applicable_synthetic",
        "scope": "fictional purchase quarter",
        "records_read": 1000,
        "expected_records": 1000,
        "duplicates": 0,
        "start": snapshot.start,
        "end": snapshot.end,
        "observed_at": snapshot.observed_at,
        "missing_fields": ["checkout_promise", "delivery", "line_quantities", "refund_feed"]
        if unknown
        else [],
        "idempotency": "same fixture/version produces same private snapshot",
        "limitations": "Not real Shopify. Carrier/promise signals are independent synthetic inputs; "
        "Shopify fulfillment timestamps cannot supply them.",
    }
    return snapshot, receipt


def without_delivery(snapshot: Snapshot) -> Snapshot:
    return replace(
        snapshot,
        orders=tuple(
            replace(o, delivered_at=None, delivery_evidence="none", delivered=None) for o in snapshot.orders
        ),
    )
