"""Consumer-owned verification. Never consumes issuer /verification or /scenarios answers."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from cryptography.exceptions import InvalidSignature
from joserfc.errors import JoseError
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .adapters.shopify_mock import TENANTS
from .contract import encode, parse_json, parse_statement, MAX_BYTES
from .decision import decide, decide_with_preferences, SCENARIOS
from .provenance import TrustedKey, unb64, verify_envelope, verify_status


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_):
        raise ValueError("redirects refused")


def read_local(base, path):
    url = urlsplit(base)
    if (
        url.scheme != "http"
        or url.hostname not in ("127.0.0.1", "localhost")
        or not url.port
        or url.path
        or url.query
        or url.fragment
        or url.username
    ):
        raise ValueError("explicit loopback demo origin required")
    if not path.startswith("/v0/") or "?" in path or "#" in path or ".." in path:
        raise ValueError("invalid local resource")
    with build_opener(NoRedirect).open(Request(base + path), timeout=5) as response:
        return parse_json(response.read(MAX_BYTES + 1))


def bootstrap_local(base, destination):
    """Deliberate TOFU for fictional process, never a production identity verification."""
    raw = read_local(base, "/v0/keys")
    pinned = {
        "origin": base,
        "assumption": "EXPLICIT LOCAL FIXTURE BOOTSTRAP, not authenticated merchant identity",
        "status_public_key": raw["status_public_key"],
        "keys": raw["keys"],
        "bindings": {subject: tenant for tenant, subject in TENANTS.items()},
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Do not silently replace an existing trust decision on restart or key change.
    with destination.open("x") as out:
        json.dump(pinned, out, indent=2)
    return pinned


def consume(pinned, scenario, fetch=None, now=None, inject=None, preferences=None):
    now = now or datetime.now(timezone.utc)
    fetch = fetch or (lambda path: read_local(pinned["origin"], path))
    keys = {
        k["kid"]: TrustedKey(
            k["kid"],
            k["issuer"],
            pinned["bindings"][k["subject"]],
            k["subject"],
            Ed25519PublicKey.from_public_bytes(unb64(k["x"], 50)),
            k["valid_from"],
            k["valid_until"],
            k["revoked"],
        )
        for k in pinned["keys"]
    }
    status_key = Ed25519PublicKey.from_public_bytes(unb64(pinned["status_public_key"], 50))
    merchants, receipts = [], []
    for subject, tenant in pinned["bindings"].items():
        evidence = []
        index = fetch(f"/v0/subjects/{subject}/performance")
        # Same-origin fixed paths; index is untrusted discovery, never an arbitrary fetch URL.
        if (
            index.get("subject") != subject
            or not isinstance(index.get("statements"), list)
            or len(index["statements"]) > 10
        ):
            raise ValueError("invalid subject index")
        for path in index["statements"]:
            identity = path.removeprefix("/v0/statements/")
            if path != "/v0/statements/" + identity or not identity.startswith("fixture-") or "/" in identity:
                raise ValueError("unsafe discovered statement path")
            envelope = fetch(path + "/signature")
            if inject == "tamper":
                envelope = {**envelope, "payload": envelope["payload"][:-2] + "AA"}
            try:
                status = verify_status(fetch(path + "/status"), status_key, tenant)
                if inject == "revoke":
                    from dataclasses import replace

                    status = replace(status, consent=False)
                if inject == "stale":
                    from dataclasses import replace

                    status = replace(status, valid_until="2026-01-01T00:00:00Z")
                result = verify_envelope(envelope, keys, {identity: status}, tenant, subject, now)
                receipts.append({"statement_id": identity, **result})
                if result["current"] and result["arithmetic_consistent"]:
                    statement = parse_statement(unb64(envelope["payload"], 86000))
                    evidence.append({"statement": statement, "verification": result})
            except (ValueError, InvalidSignature, JoseError, KeyError, TypeError):
                receipts.append(
                    {"statement_id": identity, "current": False, "reason": "invalid_or_unavailable_status"}
                )
        merchants.append({"subject": subject, "evidence": evidence})
    return {
        "consumer": "independent local reference",
        "trust_assumption": pinned["assumption"],
        "decision": decide_with_preferences({"merchants": merchants}, preferences)
        if preferences is not None
        else decide({"merchants": merchants}, scenario),
        "verification_receipts": receipts,
        "source_truth": "not_established",
        "source_recomputation": "not_available_to_consumer",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trust", type=Path, default=Path("artifacts/local-trust.json"))
    parser.add_argument(
        "--bootstrap-local", action="store_true", help="Explicitly trust this fictional loopback process once"
    )
    parser.add_argument("--origin", default="http://127.0.0.1:8787")
    parser.add_argument("--scenario", choices=SCENARIOS, default="delivery")
    parser.add_argument("--budget-cents", type=int, help="Custom total budget, 1500–3000 cents")
    parser.add_argument("--priority", choices=["price", "delivery"], default="delivery")
    parser.add_argument("--threshold", type=int, choices=[75, 85, 95], default=85)
    parser.add_argument(
        "--fixture-as-of", help="Explicit synthetic verification clock (UTC); default is strict real time"
    )
    parser.add_argument(
        "--inject",
        choices=["tamper", "revoke", "stale"],
        help="Offline alteration AFTER retrieval; sends no writes",
    )
    args = parser.parse_args()
    if args.bootstrap_local:
        bootstrap_local(args.origin, args.trust)
        print(
            "Pinned ephemeral LOCAL FIXTURE keys and status authority. Not real merchant identity. Restart requires a new explicit trust file."
        )
    if not args.trust.exists():
        parser.error(
            "explicit --trust configuration required; use --bootstrap-local only for this fictional process"
        )
    pinned = parse_json(args.trust.read_bytes())
    try:
        from .model import instant

        result = consume(
            pinned,
            args.scenario,
            now=instant(args.fixture_as_of) if args.fixture_as_of else None,
            inject=args.inject,
            preferences={
                "max_price": args.budget_cents / 100,
                "min_historical_on_time": args.threshold / 100 if args.priority == "delivery" else None,
            }
            if args.budget_cents is not None
            else None,
        )
        result["verification_clock"] = args.fixture_as_of or "real current UTC"
        print(encode(result).decode())
    except Exception as error:
        raise SystemExit("Consumer failed closed: " + type(error).__name__) from error


if __name__ == "__main__":
    main()
