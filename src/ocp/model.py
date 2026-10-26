"""Private, minimized normalized fixture model. Never serialize orders to public output."""

from dataclasses import dataclass
from datetime import datetime, timezone

MAX_ORDERS = 10_000
MAX_LINES = 100
MAX_COUNT = 1_000_000


def instant(text: str) -> datetime:
    if not isinstance(text, str) or not text.endswith("Z") or len(text) > 32:
        raise ValueError("UTC Z timestamp required")
    result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if result.utcoffset() != timezone.utc.utcoffset(result):
        raise ValueError("UTC required")
    return result


def count(value):
    if type(value) is not int or not 0 <= value <= MAX_COUNT:
        raise ValueError("bounded nonnegative integer required")
    return value


@dataclass(frozen=True)
class Order:
    tenant: str
    order_id: str  # private, synthetic merchant-local ID
    purchased_at: str
    paid: bool
    test: bool
    cancelled: bool
    promise_at_checkout: str | None
    promise_recorded_at: str | None
    fulfilled_at: str | None
    delivered_at: str | None
    delivery_evidence: str  # none / merchant_assertion / synthetic_carrier
    committed: tuple[tuple[str, int], ...] | None
    fulfilled: tuple[tuple[str, int], ...] | None
    delivered: tuple[tuple[str, int], ...] | None
    refunds_settled_at: tuple[str, ...] | None  # None = feed not observed, () = observed empty


@dataclass(frozen=True)
class Snapshot:
    tenant: str
    subject: str
    start: str
    end: str
    observed_at: str
    orders: tuple[Order, ...]
    expected_orders: int  # independent synthetic inclusion ledger, not len(selected rows)
    complete: bool
    synthetic: bool = True
    country: str = "US"
    channel: str = "shipped"
    service: str = "standard"
    category: str = "general-commerce"
    refund_policy: str = "returns-accepted-60-days"


def validate_snapshot(s: Snapshot):
    if not s.synthetic or not s.tenant.startswith("fixture-") or not s.subject.startswith("fictional:"):
        raise ValueError("synthetic fixtures only; no provider/customer input allowed")
    start, end, observed = map(instant, (s.start, s.end, s.observed_at))
    if start >= end or end > observed:
        raise ValueError("invalid window")
    # Fixed, nonoverlapping calendar quarters; no arbitrary slices/differencing endpoint.
    if start.month not in (1, 4, 7, 10) or start.day != 1 or start.time().isoformat() != "00:00:00":
        raise ValueError("fixed calendar quarter required")
    expected_end = datetime(
        start.year + (start.month == 10), (start.month + 2) % 12 + 1, 1, tzinfo=timezone.utc
    )
    if end != expected_end:
        raise ValueError("fixed calendar quarter required")
    count(s.expected_orders)
    if not 0 <= len(s.orders) <= MAX_ORDERS or s.expected_orders < len(s.orders):
        raise ValueError("invalid coverage ledger or input bound")
    ids = set()
    for o in s.orders:
        if o.tenant != s.tenant:
            raise ValueError("cross-tenant order")
        if not o.order_id.startswith("synthetic-") or o.order_id in ids:
            raise ValueError("duplicate/non-synthetic order identity")
        ids.add(o.order_id)
        for flag in (o.paid, o.test, o.cancelled):
            if type(flag) is not bool:
                raise ValueError("boolean required")
        purchase = instant(o.purchased_at)
        if not start <= purchase < end:
            raise ValueError("adapter must bind exact purchase cohort")
        for t in (o.promise_at_checkout, o.promise_recorded_at, o.fulfilled_at, o.delivered_at):
            if t:
                instant(t)
        if o.delivery_evidence not in ("none", "merchant_assertion", "synthetic_carrier"):
            raise ValueError("unknown evidence origin")
        for t in (o.fulfilled_at, o.delivered_at):
            if t and not purchase <= instant(t) <= observed:
                raise ValueError("out-of-order/future outcome")
        for lines in (o.committed, o.fulfilled, o.delivered):
            if lines is not None:
                if len(lines) > MAX_LINES or len({k for k, _ in lines}) != len(lines):
                    raise ValueError("duplicate/oversize line set")
                for sku, qty in lines:
                    if not sku.startswith("fixture-sku-") or count(qty) == 0:
                        raise ValueError("invalid line item")
        if o.committed == ():
            raise ValueError("empty commitment cannot prove completeness")
        if o.refunds_settled_at is not None:
            if len(o.refunds_settled_at) > 100:
                raise ValueError("refund bound")
            for t in o.refunds_settled_at:
                if not purchase <= instant(t) <= observed:
                    raise ValueError("out-of-order/future refund")
    if s.complete and len(s.orders) != s.expected_orders:
        raise ValueError("complete snapshot contradicts inclusion ledger")
