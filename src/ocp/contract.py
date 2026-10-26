"""Strict bounded JSON parser, structural schema and independent semantic checks."""

from hashlib import sha256
import json
import math
from pathlib import Path
from datetime import timedelta
from jsonschema import Draft202012Validator, FormatChecker
from .model import instant
from .metrics import METHODS, THRESHOLD

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "spec/schemas/performance-statement.schema.json").read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
MAX_BYTES = 64_000


def duplicate_safe(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("duplicate JSON key")
        result[k] = v
    return result


def reject_constant(_):
    raise ValueError("nonfinite JSON value")


def parse_json(raw: bytes):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError("bounded UTF-8 JSON bytes required")
    try:
        result = json.loads(
            raw.decode("utf-8"), object_pairs_hook=duplicate_safe, parse_constant=reject_constant
        )

        # Explicit tree bounds also catch overflow such as 1e999 and pathological nesting.
        def visit(value, depth=0):
            if depth > 16:
                raise ValueError("JSON too deeply nested")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("nonfinite JSON value")
            if isinstance(value, (dict, list)):
                if len(value) > 100:
                    raise ValueError("JSON collection too large")
                for child in value.values() if isinstance(value, dict) else value:
                    visit(child, depth + 1)

        visit(result)
        return result
    except (UnicodeError, RecursionError, json.JSONDecodeError) as e:
        raise ValueError("invalid JSON") from e


def encode(value):
    # This is serialization, not a claimed canonicalization standard. Sign these exact bytes.
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def validate(statement):
    VALIDATOR.validate(statement)
    m = statement["metric"]
    start, end, observed, published, expires = map(
        instant,
        [
            statement["period"]["start"],
            statement["period"]["end"],
            statement["observed_at"],
            statement["published_at"],
            statement["expires_at"],
        ],
    )
    if not start < end <= observed <= published < expires:
        raise ValueError("unordered dates")
    if expires > observed + timedelta(days=statement["freshness_limit_days"]):
        raise ValueError("expiry beyond freshness limit")
    if statement["lineage"]["source_observed_at"] != statement["observed_at"]:
        raise ValueError("lineage freshness mismatch")
    if m["followup_days"] != METHODS[m["id"]]["followup_days"]:
        raise ValueError("wrong maturity policy")
    method_bytes = encode(METHODS[m["id"]])
    if statement["lineage"]["method_manifest_sha256"] != sha256(method_bytes).hexdigest():
        raise ValueError("method manifest mismatch")
    if statement["methodology_url"] != f"/v0/methods/{m['id']}/0.2.0":
        raise ValueError("method binding mismatch")
    if m["status"] == "suppressed" and not m["privacy_suppressed"]:
        raise ValueError("suppressed state requires suppression policy")
    source = statement["lineage"]["source_record_count"]
    expected = statement["lineage"]["expected_record_count"]
    if not m["privacy_suppressed"]:
        if source is None or expected is None or source > expected:
            raise ValueError("invalid source count ledger")
        if m["source_reconciled"] and source != expected:
            raise ValueError("reconciled source count contradiction")
        for field in (
            "eligible_n",
            "observed_n",
            "unknown_n",
            "censored_n",
            "cancelled_n",
            "unfulfilled_n",
            "cohort_n",
        ):
            if m[field] is not None and m[field] > source:
                raise ValueError("population exceeds source records")
        cohort = m["cohort_n"]
        if cohort is None or any(
            m[k] is None or m[k] > cohort
            for k in ("cancelled_n", "unfulfilled_n", "censored_n", "observed_n")
        ):
            raise ValueError("invalid diagnostic population")
        diagnostics = [
            m[k] for k in ("cancelled_n", "unfulfilled_n", "unknown_n", "observed_n") if m[k] is not None
        ] + [source - cohort, expected - source]
        if any(0 < cell < THRESHOLD or 0 < cohort - cell < THRESHOLD for cell in diagnostics):
            raise ValueError("sparse diagnostic privacy violation")
        if m["eligible_n"] is not None:
            if m["observed_n"] + m["unknown_n"] != m["eligible_n"]:
                raise ValueError("signal population contradiction")
            rest = m["unfulfilled_n"] if m["id"] == "order_complete_rate" else m["censored_n"]
            if m["eligible_n"] + rest != cohort:
                raise ValueError("conditional denominator contradiction")
        elif m["source_reconciled"]:
            raise ValueError("reconciled eligible population missing")
    if m["status"] == "observed":
        n, d = m["numerator"], m["denominator"]
        if not 0 <= n <= d or abs(m["value"] - n / d) > 1e-12:
            raise ValueError("arithmetic mismatch")
        if m["eligible_n"] != d or m["observed_n"] != d or m["unknown_n"] != 0 or m["coverage_fraction"] != 1:
            raise ValueError("observed population/coverage mismatch")
        if m["censored_n"] != 0 or not m["source_reconciled"]:
            raise ValueError("observed incomplete source/cohort")
        if any(0 < cell < THRESHOLD for cell in (n, d - n)):
            raise ValueError("sparse outcome privacy violation")
        if end + timedelta(days=m["followup_days"]) > observed:
            raise ValueError("immature full cohort")
    if m["privacy_suppressed"]:
        for key in (
            "eligible_n",
            "observed_n",
            "unknown_n",
            "censored_n",
            "cancelled_n",
            "unfulfilled_n",
            "coverage_fraction",
            "cohort_n",
        ):
            if m[key] is not None:
                raise ValueError("suppression leaked count")
        if (
            statement["lineage"]["source_record_count"] is not None
            or statement["lineage"]["expected_record_count"] is not None
        ):
            raise ValueError("suppression leaked lineage counts")
    if m["lower_bound"] is not None or m["upper_bound"] is not None:
        lo, hi = m["lower_bound"], m["upper_bound"]
        if m["status"] != "partial" or lo is None or hi is None or lo > hi or not m["source_reconciled"]:
            raise ValueError("invalid bounds")
        if not m["eligible_n"] or m["observed_n"] + m["unknown_n"] != m["eligible_n"]:
            raise ValueError("bound population mismatch")
        if (
            abs(lo * m["eligible_n"] - round(lo * m["eligible_n"])) > 1e-9
            or lo * m["eligible_n"] > m["observed_n"]
        ):
            raise ValueError("bound is not an integer observed success count")
        if abs((hi - lo) - m["unknown_n"] / m["eligible_n"]) > 1e-12:
            raise ValueError("bound width mismatch")
    if m["coverage_fraction"] is not None:
        if not m["eligible_n"] or abs(m["coverage_fraction"] - m["observed_n"] / m["eligible_n"]) > 1e-12:
            raise ValueError("coverage mismatch")
    return statement


def parse_statement(raw: bytes):
    return validate(parse_json(raw))
