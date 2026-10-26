"""Exact-byte Ed25519. Trust/status are supplied out of band; never fetch payload URLs."""

from base64 import urlsafe_b64encode, b64decode
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from jsonschema.exceptions import ValidationError
from joserfc import jws
from joserfc.jwk import OKPKey
from joserfc.errors import JoseError
from .contract import encode, parse_json, parse_statement
from .model import instant

STATEMENT_TYPE = "ocp-statement+jws"
STATUS_TYPE = "ocp-status+jws"


def b64(raw):
    return urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def unb64(text, limit):
    if not isinstance(text, str) or len(text) > limit or "=" in text:
        raise ValueError("bounded unpadded base64url required")
    raw = b64decode(text + "=" * (-len(text) % 4), altchars=b"-_", validate=True)
    if b64(raw) != text:
        raise ValueError("noncanonical base64url")
    return raw


@dataclass(frozen=True)
class TrustedKey:
    kid: str
    issuer: str
    tenant: str
    subject: str
    public_key: Ed25519PublicKey
    valid_from: str
    valid_until: str
    revoked: bool = False


@dataclass(frozen=True)
class CurrentStatus:
    statement_id: str
    payload_sha256: str
    tenant: str
    subject: str
    issuer: str
    state: str  # published/revoked/corrected/disputed/withheld
    consent: bool
    checked_at: str
    valid_until: str
    superseded_by: str | None = None


def parse_header(envelope, expected_type=STATEMENT_TYPE):
    if not isinstance(envelope, dict) or set(envelope) != {"protected", "payload", "signature"}:
        raise ValueError("flattened protected JWS required")
    header = parse_json(unb64(envelope["protected"], 2048))
    if not isinstance(header, dict) or set(header) != {"alg", "kid", "typ", "cty"}:
        raise ValueError("unrecognized/critical/unprotected/key-URL headers refused")
    if header["alg"] != "Ed25519" or header["typ"] != expected_type or header["cty"] != "application/json":
        raise ValueError("unsupported JWS algorithm or content type")
    if not isinstance(header["kid"], str) or len(header["kid"]) > 100:
        raise ValueError("invalid key identifier")
    unb64(envelope["payload"], 86000)
    if len(unb64(envelope["signature"], 100)) != 64:
        raise ValueError("invalid Ed25519 signature length")
    return header


def sign_jws(raw, kid, private_key, content_type):
    return jws.serialize_json(
        {"protected": {"alg": "Ed25519", "kid": kid, "typ": content_type, "cty": "application/json"}},
        raw,
        OKPKey.import_key(private_key),
        algorithms=["Ed25519"],
    )


def verify_jws(envelope, public_key, expected_type):
    parse_header(envelope, expected_type)
    return jws.deserialize_json(envelope, OKPKey.import_key(public_key), algorithms=["Ed25519"]).payload


def sign_statement(statement, kid: str, private_key: Ed25519PrivateKey):
    payload = encode(statement)
    parse_statement(payload)
    return sign_jws(payload, kid, private_key, STATEMENT_TYPE)


def verify_envelope(
    envelope,
    keys: dict[str, TrustedKey],
    statuses: dict[str, CurrentStatus],
    expected_tenant: str,
    expected_subject: str,
    now: datetime,
):
    result = {
        "verifier": "ocp-reference/0.2.0",
        "signature_valid": False,
        "current": False,
        "usable_as_synthetic_evidence": False,
        "source_truth": "not_established",
        "calculation_reproduced": False,
        "arithmetic_consistent": False,
        "independently_audited": False,
        "reason": "invalid_envelope",
    }
    try:
        if isinstance(envelope, bytes):
            envelope = parse_json(envelope)
        header = parse_header(envelope)
        key = keys.get(header["kid"])
        if not key:
            return {**result, "reason": "untrusted_key"}
        if key.kid != header["kid"] or key.tenant != expected_tenant or key.subject != expected_subject:
            return {**result, "reason": "identity_binding_mismatch"}
        if key.revoked:
            return {**result, "reason": "key_revoked"}
        raw = verify_jws(envelope, key.public_key, STATEMENT_TYPE)
        result["signature_valid"] = True
        statement = parse_statement(raw)
        result["arithmetic_consistent"] = True
        if statement["issuer"]["id"] != key.issuer or statement["subject"]["id"] != expected_subject:
            return {**result, "reason": "identity_binding_mismatch"}
        issued, expires = map(instant, (statement["published_at"], statement["expires_at"]))
        if not instant(key.valid_from) <= issued < instant(key.valid_until) or now >= instant(
            key.valid_until
        ):
            return {**result, "reason": "key_outside_validity"}
        if not issued <= now < expires:
            return {**result, "reason": "statement_not_current"}
        status = statuses.get(statement["statement_id"])
        if not status:
            return {**result, "reason": "status_unavailable"}
        if (
            status.statement_id != statement["statement_id"]
            or status.tenant != expected_tenant
            or status.subject != expected_subject
            or status.issuer != key.issuer
            or status.payload_sha256 != sha256(raw).hexdigest()
        ):
            return {**result, "reason": "status_binding_mismatch"}
        if not (
            instant(status.checked_at)
            <= now
            < instant(status.valid_until)
            <= instant(status.checked_at) + timedelta(seconds=60)
        ):
            return {**result, "reason": "status_stale"}
        if status.state != "published" or not status.consent or status.superseded_by:
            return {**result, "reason": "withdrawn_or_superseded"}
        result["current"] = True
        usable = statement["metric"]["status"] in ("observed", "partial")
        return {
            **result,
            "usable_as_synthetic_evidence": usable,
            "reason": "current_synthetic_origin_only" if usable else statement["metric"]["status"],
        }
    except (ValueError, TypeError, KeyError, InvalidSignature, ValidationError, OverflowError, JoseError):
        return result


def sign_status(status: CurrentStatus, key_revoked: bool, key):
    public = {
        field: getattr(status, field)
        for field in (
            "statement_id",
            "payload_sha256",
            "subject",
            "issuer",
            "state",
            "consent",
            "checked_at",
            "valid_until",
            "superseded_by",
        )
    }
    public["key_revoked"] = key_revoked
    raw = encode(public)
    return sign_jws(raw, "fixture-status-authority-v1", key, STATUS_TYPE)


def verify_status(envelope, pinned_status_key, expected_tenant):
    header = parse_header(envelope, STATUS_TYPE)
    if header["kid"] != "fixture-status-authority-v1":
        raise ValueError("status authority key mismatch")
    raw = verify_jws(envelope, pinned_status_key, STATUS_TYPE)
    data = parse_json(raw)
    expected = {
        "statement_id",
        "payload_sha256",
        "subject",
        "issuer",
        "state",
        "consent",
        "checked_at",
        "valid_until",
        "superseded_by",
        "key_revoked",
    }
    if (
        not isinstance(data, dict)
        or set(data) != expected
        or type(data["consent"]) is not bool
        or type(data["key_revoked"]) is not bool
    ):
        raise ValueError("invalid signed status fields")
    if data["state"] not in ("published", "revoked", "corrected", "disputed", "withheld"):
        raise ValueError("invalid status state")
    if data.pop("key_revoked"):
        data["state"] = "revoked"
    return CurrentStatus(**data, tenant=expected_tenant)
