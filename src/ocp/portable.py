"""Bounded portable-evidence preview. Fictional sources, ephemeral keys, no writes or remote fetches."""

from copy import deepcopy
from datetime import timedelta
from hashlib import sha256

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from joserfc.errors import JoseError

from .contract import ROOT, encode, parse_json
from .model import instant
from .provenance import (
    CurrentStatus,
    TrustedKey,
    parse_header,
    sign_jws,
    sign_status,
    verify_jws,
    verify_status,
)

TYPE = "ocp-portable-claim+jws"
SCHEMA = parse_json((ROOT / "spec/schemas/portable-claim.schema.json").read_bytes())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
ISSUER = "fictional:evidence-service"
ISSUED = "2026-10-25T20:00:00Z"
EXPIRES = "2026-11-01T20:00:00Z"


def method(name, field, unit, aggregation, population, limit):
    return {
        "id": "https://example.invalid/methods/" + name,
        "version": "0.1.0",
        "title": name,
        "field": field,
        "unit": unit,
        "aggregation": aggregation,
        "formula": "sum(recorded values) / observed_count",
        "population": population,
        "exclusions": ["Test records"],
        "missing": "No point estimate when eligible observations are missing.",
        "privacy": "Synthetic aggregates only; real release privacy requires a separate policy.",
        "limit": limit,
    }


METHODS = {
    "net-check": method(
        "average-net-check",
        "net_cents",
        "USD cents per check",
        "mean",
        "All paid non-test checks in the fictional POS location and period; net of discounts; tax and tip excluded.",
        "A check is not a person or party; modifiers and meal mix affect spending.",
    ),
    "pickup": method(
        "pickup-preparation",
        "pickup_minutes",
        "minutes",
        "mean",
        "All accepted pickup orders at this location in the period; acceptance to recorded ready event.",
        "Recorded readiness does not establish handoff, arrival, food quality or peak-hour performance.",
    ),
    "delivery": method(
        "original-promise-delivery",
        "on_time",
        "fraction",
        "rate",
        "All accepted shipped orders in the period, with original promises and full recorded carrier follow-up.",
        "Historical delivery observations are not a future guarantee or evidence of product quality.",
    ),
    "dispatch": method(
        "order-dispatch-time",
        "dispatch_hours",
        "hours",
        "mean",
        "All accepted shipped orders in the period; acceptance to recorded carrier handoff.",
        "Dispatch is not delivery. This average does not describe the slowest orders.",
    ),
    "response": method(
        "first-support-response",
        "response_minutes",
        "elapsed minutes",
        "mean",
        "All new customer support inquiries in the period; receipt to first recorded human response.",
        "Automated replies excluded. Response is not resolution or customer satisfaction.",
    ),
    "quote": method(
        "invoice-within-quote",
        "within_quote",
        "fraction",
        "rate",
        "All completed fixed-scope jobs in the period; final invoice compared with the accepted quote for that scope.",
        "Does not establish workmanship, project speed or the fairness of the quoted price.",
    ),
}
BUSINESSES = {
    "restaurant": {
        "name": "Juniper Kitchen",
        "type": "Restaurant",
        "source": "Fictional POS export",
        "metrics": ["net-check", "pickup"],
        "needs": [
            {"id": "pickup", "label": "A quick lunch pickup", "metric": "pickup", "max": 20},
            {
                "id": "net-check",
                "label": "Understand typical check spending",
                "metric": "net-check",
                "max": 3000,
            },
        ],
        "unknowns": "Today's availability, party size, food quality and dietary suitability remain unanswered.",
    },
    "ecommerce": {
        "name": "Fieldwork Goods",
        "type": "Ecommerce brand",
        "source": "Fictional order and carrier records",
        "metrics": ["delivery", "dispatch"],
        "needs": [
            {"id": "delivery", "label": "A dependable delivery history", "metric": "delivery", "min": 0.9},
            {
                "id": "dispatch",
                "label": "Orders dispatched within a day on average",
                "metric": "dispatch",
                "max": 24,
            },
        ],
        "unknowns": "Current stock, your delivery promise, return terms and product suitability remain unanswered.",
    },
    "b2b": {
        "name": "Northline Services",
        "type": "B2B service company",
        "source": "Fictional CRM and billing export",
        "metrics": ["response", "quote"],
        "needs": [
            {"id": "response", "label": "Responsive customer support", "metric": "response", "max": 60},
            {
                "id": "quote",
                "label": "Invoices consistent with accepted quotes",
                "metric": "quote",
                "min": 0.95,
            },
        ],
        "unknowns": "Your project scope, current capacity, workmanship and resolution quality remain unanswered.",
    },
}


def validate_claim(claim, methods):
    VALIDATOR.validate(claim)
    manifest = methods.get(claim["method"]["id"])
    if not manifest or claim["method"]["version"] != manifest["version"]:
        raise ValueError("method_not_understood")
    if claim["method"]["sha256"] != sha256(encode(manifest)).hexdigest():
        raise ValueError("method_digest_mismatch")
    p, result = claim["population"], claim["result"]
    if p["eligibility"] != manifest["population"] or p["exclusions"] != manifest["exclusions"]:
        raise ValueError("method_population_mismatch")
    if p["observed_count"] + p["missing_count"] != p["eligible_count"]:
        raise ValueError("population_mismatch")
    if result["unit"] != manifest["unit"] or result["aggregation"] != manifest["aggregation"]:
        raise ValueError("method_result_mismatch")
    observed = p["eligible_count"] > 0 and p["missing_count"] == 0
    if (result["state"] == "observed") != observed:
        raise ValueError("observation_state_mismatch")
    if observed != (result["value"] is not None):
        raise ValueError("unknown_is_not_a_number")
    if result["aggregation"] == "rate" and result["value"] is not None and result["value"] > 1:
        raise ValueError("invalid_fraction")
    dates = [instant(claim[k]) for k in ("observed_at", "issued_at", "expires_at")]
    if not instant(p["start"]) < instant(p["end"]) <= dates[0] <= dates[1] < dates[2]:
        raise ValueError("unordered_dates")


def verify_claim(envelope, status_envelope, key, status_key, subject, methods, now):
    """Consumer-side check with explicitly supplied local trust; never read raw source records."""
    result = {
        "usable": False,
        "signature_valid": False,
        "current": False,
        "source_truth": "not_established",
        "independently_audited": False,
    }
    try:
        header = parse_header(envelope, TYPE)
        if header["kid"] != key.kid or key.subject != subject or key.revoked:
            raise ValueError("untrusted_identity")
        raw = verify_jws(envelope, key.public_key, TYPE)
        result["signature_valid"] = True
        claim = parse_json(raw)
        validate_claim(claim, methods)
        if claim["subject"]["id"] != subject or claim["issuer"]["id"] != key.issuer:
            raise ValueError("identity_binding_mismatch")
        # This fixture key is authorized only for service calculations, never provider endorsement.
        assurance = claim["assurance"]
        if (
            not claim["synthetic"]
            or assurance["kind"] != "service_calculated"
            or assurance["provider_endorsed"]
            or assurance["independent_audit"]
            or assurance["source_accuracy"] != "not_established"
        ):
            raise ValueError("assurance_exceeds_fixture_authority")
        issued = instant(claim["issued_at"])
        if (
            not instant(key.valid_from)
            <= issued
            <= now
            < min(instant(key.valid_until), instant(claim["expires_at"]))
        ):
            raise ValueError("claim_not_current")
        status = verify_status(status_envelope, status_key, key.tenant)
        if (
            status.statement_id != claim["claim_id"]
            or status.subject != subject
            or status.issuer != key.issuer
            or status.payload_sha256 != sha256(raw).hexdigest()
        ):
            raise ValueError("status_binding_mismatch")
        if (
            not instant(status.checked_at)
            <= now
            < instant(status.valid_until)
            <= instant(status.checked_at) + timedelta(seconds=60)
        ):
            raise ValueError("status_not_current")
        if status.state != "published" or not status.consent or status.superseded_by:
            raise ValueError("withdrawn_or_disputed")
        result["current"] = True
        return {
            **result,
            "usable": claim["result"]["state"] == "observed",
            "reason": "checked_synthetic_claim",
        }
    except (
        ValueError,
        TypeError,
        KeyError,
        InvalidSignature,
        ValidationError,
        OverflowError,
        JoseError,
    ) as error:
        # Untrusted input must not leave a previous successful result on screen.
        return {**result, "reason": type(error).__name__ + ": " + str(error)[:100]}


class PortablePreview:
    def __init__(self):
        self.status_key = Ed25519PrivateKey.generate()
        self.private = {name: Ed25519PrivateKey.generate() for name in BUSINESSES}
        self.keys = {
            name: TrustedKey(
                "portable-" + name,
                ISSUER,
                "fixture-" + name,
                "fictional:" + name,
                private.public_key(),
                "2026-10-25T00:00:00Z",
                EXPIRES,
            )
            for name, private in self.private.items()
        }
        self.rows = [
            {
                "net_cents": 2200 + (i % 5) * 200,
                "pickup_minutes": 10 + i % 9,
                "on_time": int(i < 94),
                "dispatch_hours": 12 + i % 24,
                "response_minutes": 10 + i % 41,
                "within_quote": int(i < 97),
            }
            for i in range(100)
        ]

    def claim(self, business, metric):
        b, m = BUSINESSES[business], METHODS[metric]
        values = [row[m["field"]] for row in self.rows if row.get(m["field"]) is not None]
        complete = len(values) == len(self.rows) and bool(values)
        return {
            "schema_version": "0.3.0",
            "synthetic": True,
            "claim_id": "fictional:" + business + ":" + metric + ":2026-10",
            "subject": {"id": "fictional:" + business, "name": b["name"]},
            "issuer": {
                "id": ISSUER,
                "name": "Fictional evidence service",
                "relationship": "Business-authorized calculation service; no provider endorsement.",
            },
            "method": {"id": m["id"], "version": m["version"], "sha256": sha256(encode(m)).hexdigest()},
            "population": {
                "start": "2026-10-01T00:00:00Z",
                "end": "2026-10-25T00:00:00Z",
                "service": b["type"],
                "eligibility": m["population"],
                "exclusions": ["Test records"],
                "eligible_count": len(self.rows),
                "observed_count": len(values),
                "missing_count": len(self.rows) - len(values),
            },
            "result": {
                "value": sum(values) / len(values) if complete else None,
                "unit": m["unit"],
                "aggregation": m["aggregation"],
                "state": "observed" if complete else "unknown",
            },
            "assurance": {
                "kind": "service_calculated",
                "source_name": b["source"],
                "provider_endorsed": False,
                "checks": [
                    "Calculation reproduced on generated records",
                    "Declared synthetic population reconciled",
                ],
                "source_accuracy": "not_established",
                "independent_audit": False,
            },
            "observed_at": "2026-10-25T12:00:00Z",
            "issued_at": ISSUED,
            "expires_at": EXPIRES,
            "limitations": [
                m["limit"],
                "Fictional records; no real business, provider or AI platform is connected.",
            ],
        }

    def preview(self, business, selected, state, need, now):
        if business not in BUSINESSES or state not in ("published", "withdrawn", "disputed"):
            raise ValueError("unknown business or preview state")
        b = BUSINESSES[business]
        if len(selected) != len(set(selected)) or not set(selected) <= set(b["metrics"]):
            raise ValueError("unsupported or duplicate metric")
        requirement = next((n for n in b["needs"] if n["id"] == need), None)
        if requirement is None:
            raise ValueError("unsupported buyer need")
        evidence = []
        manifests = {m["id"]: m for m in METHODS.values()}
        for metric in sorted(selected):
            claim = self.claim(business, metric)
            validate_claim(claim, manifests)
            raw = encode(claim)
            envelope = sign_jws(raw, self.keys[business].kid, self.private[business], TYPE)
            status = CurrentStatus(
                claim["claim_id"],
                sha256(raw).hexdigest(),
                "fixture-" + business,
                claim["subject"]["id"],
                ISSUER,
                "revoked" if state == "withdrawn" else state,
                state != "withdrawn",
                now.isoformat().replace("+00:00", "Z"),
                (now + timedelta(seconds=60)).isoformat().replace("+00:00", "Z"),
            )
            signed_status = sign_status(status, False, self.status_key)
            checked = verify_claim(
                envelope,
                signed_status,
                self.keys[business],
                self.status_key.public_key(),
                claim["subject"]["id"],
                manifests,
                now,
            )
            reproduced = self.claim(business, metric)["result"] == claim["result"]
            evidence.append(
                {
                    "metric": metric,
                    "claim": claim,
                    "envelope": envelope,
                    "signed_status": signed_status,
                    "verification": checked,
                    "publisher_reproduced": reproduced,
                }
            )
        applicable = next((e for e in evidence if e["metric"] == need and e["verification"]["usable"]), None)
        supported = False
        if applicable:
            value = applicable["claim"]["result"]["value"]
            supported = value >= requirement["min"] if "min" in requirement else value <= requirement["max"]
        return {
            "preview_only": True,
            "synthetic": True,
            "live_registry_changed": False,
            "demo_clock": now.isoformat().replace("+00:00", "Z"),
            "business_id": business,
            "business": deepcopy(b),
            "available": [{"id": key, "definition": deepcopy(METHODS[key])} for key in b["metrics"]],
            "selected": sorted(selected),
            "state": state,
            "evidence": evidence,
            "assessment": {
                "state": "supports_consideration"
                if supported
                else "not_supported"
                if applicable
                else "unknown",
                "need": need,
                "cited_claims": [applicable["claim"]["claim_id"]] if applicable else [],
                "threshold": requirement.get("min", requirement.get("max")),
                "unknowns": b["unknowns"],
                "market_coverage": "not_established",
                "kind": "Deterministic evidence interpretation; no LLM or market search.",
            },
        }
