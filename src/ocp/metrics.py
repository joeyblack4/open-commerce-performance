"""Pure deterministic calculations; no clocks, network, credentials, or global state."""

from datetime import timedelta
from .model import Snapshot, instant, validate_snapshot

VERSION = "0.2.0"
THRESHOLD = 30
METHODS = {
    "fulfilled_on_time_rate": {
        "label": "Delivered on time and in full",
        "followup_days": 30,
        "definition": "Paid non-test purchase-quarter orders mature for 30 days. Original checkout promise, "
        "separately sourced final delivery and exact delivered quantities required. "
        "Cancelled orders remain in population; unresolved outcomes remain unknown.",
        "limitation": "Synthetic carrier records only; no real carrier or independent audit. "
        "Shipment timestamps are never delivery evidence.",
    },
    "order_complete_rate": {
        "label": "Complete at recorded fulfillment",
        "followup_days": 0,
        "definition": "Paid non-test purchase-quarter orders reaching recorded fulfillment by observation. "
        "Exact committed versus fulfilled SKU quantities. Cancelled/unfulfilled orders counted "
        "outside this conditional denominator, never called delivered.",
        "limitation": "Recorded fulfillment is not confirmed consumer delivery or physical product quality.",
    },
    "order_refund_incidence": {
        "label": "Orders with settled refunds",
        "followup_days": 60,
        "definition": "Paid non-test purchase-quarter orders with 60 full days observation. Count once per "
        "order with any settled refund in [purchase, purchase+60 days). Cancellations retained.",
        "limitation": "Refund incidence is not defect incidence or satisfaction. Denied returns, store credit, "
        "chargebacks and policy friction are not measured; lower is not automatically better.",
    },
}


def calculate(s: Snapshot, metric_id: str) -> dict:
    validate_snapshot(s)
    if metric_id not in METHODS:
        raise ValueError("unsupported metric; repeat/physical reliability deferred")
    method = METHODS[metric_id]
    observed = instant(s.observed_at)
    cohort = [o for o in s.orders if o.paid and not o.test]
    mature = [
        o for o in cohort if instant(o.purchased_at) + timedelta(days=method["followup_days"]) <= observed
    ]
    eligible = [o for o in mature if o.fulfilled_at] if metric_id == "order_complete_rate" else mature
    known, positive, conflicts = 0, 0, 0
    for o in eligible:
        result = None
        if metric_id == "fulfilled_on_time_rate":
            if o.promise_at_checkout and o.promise_recorded_at:
                promise = instant(o.promise_at_checkout)
                committed_at = instant(o.promise_recorded_at)
                # A later edited promise, including backdating without an immutable source, cannot prove success.
                if committed_at != instant(o.purchased_at) or promise < committed_at:
                    conflicts += 1
                elif (
                    o.delivered_at
                    and o.delivery_evidence == "synthetic_carrier"
                    and o.committed
                    and o.delivered is not None
                ):
                    result = instant(o.delivered_at) <= promise and dict(o.committed) == dict(o.delivered)
        elif metric_id == "order_complete_rate":
            if o.committed and o.fulfilled is not None:
                result = dict(o.committed) == dict(o.fulfilled)
        elif o.refunds_settled_at is not None:
            limit = instant(o.purchased_at) + timedelta(days=60)
            result = any(instant(o.purchased_at) <= instant(t) < limit for t in o.refunds_settled_at)
        if result is not None:
            known += 1
            positive += int(result)
    total = len(eligible)
    unknown = total - known
    censored = len(cohort) - len(mature)
    # Missing entire source rows make the actual eligible denominator unknown. Never invent bounds.
    reconciled = s.complete and len(s.orders) == s.expected_orders
    status = "observed" if reconciled and total and known == total and not censored else "partial"
    if not total or not known:
        status = "not_observed"
    # Release policy suppresses cohorts AND sparse outcome/complement cells and any immature cohort.
    diagnostics = [
        sum(o.cancelled for o in cohort),
        sum(not o.fulfilled_at for o in cohort),
        unknown,
        known,
        len(s.orders) - len(cohort),
        s.expected_orders - len(s.orders),
    ]
    sparse_diagnostic = any(
        0 < cell < THRESHOLD or 0 < len(cohort) - cell < THRESHOLD for cell in diagnostics
    )
    suppressed = bool(
        total < THRESHOLD
        or censored
        or sparse_diagnostic
        or (0 < positive < THRESHOLD)
        or (0 < known - positive < THRESHOLD)
    )
    if suppressed and (known or total or censored or 0 < len(cohort) < THRESHOLD):
        status = "suppressed"
    if conflicts:
        status = "disputed"
    numeric = status == "observed"
    bounds = status == "partial" and reconciled and total >= THRESHOLD and not suppressed
    coverage = known / total if total and not suppressed and reconciled else None
    return {
        "id": metric_id,
        "definition_version": VERSION,
        "status": status,
        "unit": "fraction",
        "numerator": positive if numeric else None,
        "denominator": total if numeric else None,
        "value": positive / total if numeric else None,
        "lower_bound": positive / total if bounds else None,
        "upper_bound": (positive + unknown) / total if bounds else None,
        "coverage_fraction": coverage,
        "eligible_n": total if not suppressed and reconciled else None,
        "observed_n": known if not suppressed else None,
        "unknown_n": unknown if not suppressed and reconciled else None,
        "censored_n": censored if not suppressed else None,
        "cohort_n": len(cohort) if not suppressed else None,
        "cancelled_n": sum(o.cancelled for o in cohort) if not suppressed else None,
        "unfulfilled_n": sum(not o.fulfilled_at for o in cohort) if not suppressed else None,
        "followup_days": method["followup_days"],
        "minimum_public_cohort": THRESHOLD,
        "privacy_suppressed": suppressed,
        "source_reconciled": reconciled,
        "reason": (
            "conflicting checkout promise"
            if conflicts
            else "cohort/outcome privacy or maturation suppression"
            if suppressed
            else "source rows incomplete; eligible denominator unknown"
            if not reconciled
            else "required signals missing"
            if unknown or not total
            else "exact observed synthetic calculation"
        ),
    }


def compare(a: dict, b: dict) -> dict:
    """Comparability only. Never a rank/score; missing evidence never penalizes a merchant."""
    fields = ("schema_version", "period", "comparison", "refund_policy")
    same = all(a[k] == b[k] for k in fields) and a["metric"]["id"] == b["metric"]["id"]
    current = a["metric"]["status"] == b["metric"]["status"] == "observed"
    return {
        "comparable": same and current,
        "reason": "matching scope and observed methods"
        if same and current
        else "not comparable: scope/policy/method/observation differs",
        "ranking": None,
    }
