"""In-memory fixture registry. No durable consent/identity store or admin API."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from .adapters.shopify_mock import TENANTS, read_snapshot
from .contract import encode
from .metrics import METHODS
from .provenance import CurrentStatus, TrustedKey, sign_statement, verify_envelope, sign_status, parse_header
from .statements import ISSUER, make_statement, reproduce


class Registry:
    def __init__(self):
        # Ephemeral per-process keys, never exported or committed. Restart creates a fresh trust domain.
        self.private_keys = {}
        self.status_private_key = Ed25519PrivateKey.generate()
        self.keys = {}
        self.statements = {}
        self.envelopes = {}
        self.snapshots = {}
        self.lifecycle = {}
        self.ownership = {}
        self.consent = dict.fromkeys(TENANTS, True)
        for tenant, subject in TENANTS.items():
            kid = tenant + "-ephemeral-1"
            private_key = Ed25519PrivateKey.generate()
            self.private_keys[tenant] = private_key
            self.keys[kid] = TrustedKey(
                kid,
                ISSUER,
                tenant,
                subject,
                private_key.public_key(),
                "2026-10-25T00:00:00Z",
                "2026-11-02T00:00:00Z",
            )
            snapshot, _ = read_snapshot(tenant)
            self.snapshots[tenant] = snapshot
            for metric_id in METHODS:
                s = make_statement(snapshot, metric_id)
                identity = s["statement_id"]
                self.statements[identity] = s
                self.ownership[identity] = (tenant, subject)
                self.envelopes[identity] = sign_statement(s, kid, private_key)
                self.lifecycle[identity] = {"state": "published", "superseded_by": None}

    def current_status(self, identity, now):
        if identity not in self.ownership:
            raise KeyError("unknown statement")
        tenant, subject = self.ownership[identity]
        return CurrentStatus(
            identity,
            sha256(encode(self.statements[identity])).hexdigest(),
            tenant,
            subject,
            ISSUER,
            self.lifecycle[identity]["state"],
            self.consent[tenant],
            now.isoformat().replace("+00:00", "Z"),
            (now + timedelta(seconds=60)).isoformat().replace("+00:00", "Z"),
            self.lifecycle[identity]["superseded_by"],
        )

    def signed_status(self, identity, now):
        return sign_status(
            self.current_status(identity, now),
            self.keys[parse_header(self.envelopes[identity])["kid"]].revoked,
            self.status_private_key,
        )

    def verification(self, identity, now=None):
        now = now or datetime.now(timezone.utc)
        tenant, subject = self.ownership[identity]
        status = self.current_status(identity, now)
        result = verify_envelope(
            self.envelopes[identity], self.keys, {identity: status}, tenant, subject, now
        )
        result["calculation_reproduced"] = reproduce(self.statements[identity], self.snapshots[tenant])
        return result

    def withdraw(self, tenant):
        if tenant not in self.consent:
            raise KeyError("unknown tenant")
        self.consent[tenant] = False
        for identity, (owner, _) in self.ownership.items():
            if owner == tenant:
                self.lifecycle[identity]["state"] = "revoked"

    def revoke_key(self, kid):
        self.keys[kid] = replace(self.keys[kid], revoked=True)

    def get_public(self, identity, now=None):
        verification = self.verification(identity, now)
        if not verification["current"]:
            return None
        return {
            "statement": self.statements[identity],
            "envelope": self.envelopes[identity],
            "verification": verification,
        }

    def bundle(self, now=None):
        rows = []
        for tenant, subject in TENANTS.items():
            evidence = [self.get_public(i, now) for i, (t, _) in self.ownership.items() if t == tenant]
            rows.append(
                {
                    "subject": subject,
                    "name": {
                        "fixture-a": "Cedar Market",
                        "fixture-b": "Grove Goods",
                        "fixture-unknown": "Little Pantry",
                    }[tenant],
                    "evidence": [x for x in evidence if x],
                }
            )
        return {
            "experimental": True,
            "synthetic": True,
            "merchants": rows,
            "limitations": "Fictional demonstration. No independent audit, real merchant data or ranking.",
        }
