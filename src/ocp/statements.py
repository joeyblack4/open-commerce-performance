"""Explicit allowlist projection: no raw IDs, lines, arbitrary notes or source text."""

from hashlib import sha256
from datetime import timedelta
from .contract import encode, validate
from .metrics import calculate, METHODS, VERSION
from .model import Snapshot, instant

ISSUER = "https://example.invalid/black4-fixture-issuer"


def make_statement(snapshot: Snapshot, metric_id: str):
    m = calculate(snapshot, metric_id)
    suppressed = m["privacy_suppressed"]
    statement = {
        "schema_version": VERSION,
        "experimental": True,
        "synthetic": True,
        "statement_id": f"{snapshot.tenant}-{metric_id.replace('_', '-')}-{snapshot.start[:10].replace('-', '')}-{snapshot.end[:10].replace('-', '')}-v020",
        "subject": {"type": "merchant", "id": snapshot.subject},
        "issuer": {
            "id": ISSUER,
            "role": "research_fixture",
            "financial_relationship": "Black 4 local synthetic research; no placement or affiliate payments",
        },
        "metric": m,
        "period": {"start": snapshot.start, "end": snapshot.end, "end_exclusive": True},
        "observed_at": snapshot.observed_at,
        "published_at": snapshot.observed_at,
        "expires_at": (instant(snapshot.observed_at) + timedelta(days=7)).isoformat().replace("+00:00", "Z"),
        "freshness_limit_days": 7,
        "comparison": {
            "country": snapshot.country,
            "channel": snapshot.channel,
            "service": snapshot.service,
            "category": snapshot.category,
            "population": "paid non-test orders in purchase calendar quarter; cancellations retained",
        },
        "refund_policy": {
            "id": snapshot.refund_policy,
            "as_of": snapshot.start,
            "url": "https://example.invalid/refund-policy",
        },
        "lineage": {
            "source_type": "synthetic",
            "access_mode": "synthetic_read_only",
            "adapter_version": "shopify_mock/0.2.0",
            "source_observed_at": snapshot.observed_at,
            "source_record_count": None if suppressed else len(snapshot.orders),
            "expected_record_count": None if suppressed else snapshot.expected_orders,
            "method_manifest_sha256": sha256(encode(METHODS[metric_id])).hexdigest(),
        },
        "assurance": {
            "source_authenticated": False,
            "calculation_reproduced": False,
            "independent_corroboration": False,
            "independently_audited": False,
            "limitations": "Synthetic fixture only. Signature proves signed origin, not source truth, "
            "completeness, delivery or audit. Calculation reproduction is computed separately.",
        },
        "status": "published",
        "methodology_url": f"/v0/methods/{metric_id}/{VERSION}",
    }
    return validate(statement)


def reproduce(statement, snapshot):
    """Requires private authorized snapshot. Public bytes alone cannot reproduce source truth."""
    try:
        validate(statement)
        return statement == make_statement(snapshot, statement["metric"]["id"])
    except (ValueError, KeyError):
        return False
