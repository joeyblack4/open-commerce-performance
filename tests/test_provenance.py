from dataclasses import replace
from hashlib import sha256
from datetime import timedelta
import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from joserfc.errors import JoseError
from ocp.contract import encode
from ocp.model import instant
from ocp.provenance import TrustedKey, sign_statement, verify_envelope, verify_status, b64, parse_header
from ocp.registry import Registry
from ocp.statements import reproduce

NOW = instant("2026-10-25T20:00:00Z")


class ProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()
        cls.identity = next(iter(cls.registry.ownership))
        cls.envelope = cls.registry.envelopes[cls.identity]
        cls.tenant, cls.subject = cls.registry.ownership[cls.identity]

    def verify(self, envelope=None, keys=None, statuses=None, tenant=None, subject=None, now=NOW):
        r = self.registry
        return verify_envelope(
            self.envelope if envelope is None else envelope,
            r.keys if keys is None else keys,
            {self.identity: r.current_status(self.identity, NOW)} if statuses is None else statuses,
            tenant or self.tenant,
            subject or self.subject,
            now,
        )

    def test_valid_origin_is_not_source_truth(self):
        v = self.verify()
        self.assertTrue(v["signature_valid"])
        self.assertTrue(v["current"])
        self.assertTrue(v["arithmetic_consistent"])
        self.assertEqual(v["source_truth"], "not_established")
        self.assertFalse(v["calculation_reproduced"])
        self.assertFalse(v["independently_audited"])

    def test_tampered_bytes_signature_and_algorithm(self):
        for change in [
            {"payload": self.envelope["payload"][:-4] + "AAAA"},
            {"signature": b64(b"\0" * 64)},
            {"alg": "none"},
            {"alg": "HS256"},
            {"format": "W3C-VC"},
        ]:
            v = self.verify({**self.envelope, **change})
            self.assertFalse(v["current"])

    def test_unknown_key_cross_tenant_and_subject(self):
        self.assertFalse(self.verify(keys={})["current"])
        self.assertFalse(self.verify(tenant="fixture-b")["current"])
        self.assertFalse(self.verify(subject="fictional:merchant-b")["current"])
        v = self.verify({**self.envelope, "kid": "fixture-b-ephemeral-1"})
        self.assertFalse(v["signature_valid"])

    def test_issuer_binding_and_revoked_key(self):
        kid = parse_header(self.envelope)["kid"]
        keys = dict(self.registry.keys)
        keys[kid] = replace(keys[kid], issuer="https://attacker.invalid")
        self.assertFalse(self.verify(keys=keys)["current"])
        keys[kid] = replace(self.registry.keys[kid], revoked=True)
        self.assertEqual(self.verify(keys=keys)["reason"], "key_revoked")

    def test_key_issue_and_expiry_bounds(self):
        kid = parse_header(self.envelope)["kid"]
        keys = dict(self.registry.keys)
        for start, end in [
            ("2026-10-26T00:00:00Z", "2026-11-02T00:00:00Z"),
            ("2026-10-01T00:00:00Z", "2026-10-25T19:00:00Z"),
        ]:
            keys[kid] = replace(self.registry.keys[kid], valid_from=start, valid_until=end)
            self.assertEqual(self.verify(keys=keys)["reason"], "key_outside_validity")

    def test_rotation_can_verify_both_keys_with_explicit_trust(self):
        private = Ed25519PrivateKey.generate()
        kid = "fixture-a-ephemeral-2"
        old = self.registry.keys[parse_header(self.envelope)["kid"]]
        keys = {
            **self.registry.keys,
            kid: TrustedKey(
                kid,
                old.issuer,
                old.tenant,
                old.subject,
                private.public_key(),
                old.valid_from,
                old.valid_until,
            ),
        }
        self.assertTrue(self.verify(keys=keys)["current"])
        envelope = sign_statement(self.registry.statements[self.identity], kid, private)
        self.assertTrue(self.verify(envelope, keys=keys)["current"])

    def test_no_status_stale_future_or_unbounded_status_ttl(self):
        self.assertEqual(self.verify(statuses={})["reason"], "status_unavailable")
        base = self.registry.current_status(self.identity, NOW)
        for s in [
            replace(base, valid_until="2026-10-25T19:00:00Z"),
            replace(base, checked_at="2026-10-25T21:00:00Z"),
            replace(base, valid_until="2026-10-26T00:00:00Z"),
        ]:
            self.assertEqual(self.verify(statuses={self.identity: s})["reason"], "status_stale")

    def test_expiry_and_future_publication(self):
        self.assertEqual(self.verify(now=NOW - timedelta(days=1))["reason"], "statement_not_current")
        self.assertEqual(self.verify(now=NOW + timedelta(days=7))["reason"], "statement_not_current")

    def test_status_digest_binding_revoke_dispute_and_correction(self):
        status = self.registry.current_status(self.identity, NOW)
        for s in [
            replace(status, consent=False),
            replace(status, state="revoked"),
            replace(status, state="disputed"),
            replace(status, state="withheld"),
            replace(status, superseded_by="fixture-corrected-0001"),
        ]:
            self.assertEqual(self.verify(statuses={self.identity: s})["reason"], "withdrawn_or_superseded")
        self.assertEqual(
            self.verify(statuses={self.identity: replace(status, payload_sha256="0" * 64)})["reason"],
            "status_binding_mismatch",
        )

    def test_validly_signed_false_claim_not_reproduced(self):
        s = copy.deepcopy(self.registry.statements[self.identity])
        s["metric"]["numerator"] = 750
        s["metric"]["value"] = 0.75
        envelope = sign_statement(
            s, parse_header(self.envelope)["kid"], self.registry.private_keys[self.tenant]
        )
        status = replace(
            self.registry.current_status(self.identity, NOW), payload_sha256=sha256(encode(s)).hexdigest()
        )
        result = self.verify(envelope, statuses={self.identity: status})
        self.assertTrue(result["signature_valid"])
        self.assertTrue(result["arithmetic_consistent"])
        self.assertEqual(result["source_truth"], "not_established")
        self.assertFalse(reproduce(s, self.registry.snapshots[self.tenant]))

    def test_signed_status_independent_authority(self):
        signed = self.registry.signed_status(self.identity, NOW)
        verified = verify_status(signed, self.registry.status_private_key.public_key(), self.tenant)
        self.assertEqual(verified, self.registry.current_status(self.identity, NOW))
        signed["payload"] = signed["payload"][:-3] + "AAA"
        with self.assertRaises((JoseError, ValueError)):
            verify_status(signed, self.registry.status_private_key.public_key(), self.tenant)

    def test_consent_withdrawal_removes_all_claims(self):
        registry = Registry()
        other_ids = [i for i, (tenant, _) in registry.ownership.items() if tenant == "fixture-b"]
        registry.withdraw("fixture-a")
        for i, (tenant, _) in registry.ownership.items():
            self.assertEqual(registry.get_public(i, NOW) is None, tenant == "fixture-a")
        for i in other_ids:
            self.assertIsNotNone(registry.get_public(i, NOW))

    def test_unknown_metric_never_usable_even_when_signed(self):
        r = self.registry
        identity = next(i for i, (t, _) in r.ownership.items() if t == "fixture-unknown")
        v = r.verification(identity, NOW)
        self.assertTrue(v["signature_valid"])
        self.assertTrue(v["current"])
        self.assertFalse(v["usable_as_synthetic_evidence"])


class JwsProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()
        cls.identity = next(iter(cls.registry.ownership))
        cls.tenant, cls.subject = cls.registry.ownership[cls.identity]
        cls.envelope = cls.registry.envelopes[cls.identity]

    def signed_header(self, raw):
        protected = b64(raw)
        payload = self.envelope["payload"]
        signature = self.registry.private_keys[self.tenant].sign((protected + "." + payload).encode("ascii"))
        return {"protected": protected, "payload": payload, "signature": b64(signature)}

    def test_protected_header_attack_fixtures_even_if_signed(self):
        header = parse_header(self.envelope)
        for mutation in [
            {"alg": "none"},
            {"alg": "EdDSA"},
            {"alg": "HS256"},
            {"jku": "https://attacker.invalid"},
            {"jwk": {"kty": "OKP"}},
            {"crit": ["unknown"]},
            {"b64": False},
            {"typ": "JWT"},
            {"cty": "text/plain"},
        ]:
            envelope = self.signed_header(encode({**header, **mutation}))
            v = verify_envelope(
                envelope,
                self.registry.keys,
                {self.identity: self.registry.current_status(self.identity, NOW)},
                self.tenant,
                self.subject,
                NOW,
            )
            self.assertFalse(v["current"], mutation)
        duplicate = b'{"alg":"none","alg":"Ed25519","kid":"fixture-a-ephemeral-1","typ":"ocp-statement+jws","cty":"application/json"}'
        with self.assertRaises(ValueError):
            parse_header(self.signed_header(duplicate))
        for envelope in [
            {**self.envelope, "header": {"kid": "other"}},
            {**self.envelope, "protected": self.envelope["protected"] + "="},
        ]:
            with self.assertRaises(ValueError):
                parse_header(envelope)

    def test_independent_node_crypto_interoperability(self):
        import json
        import subprocess
        from ocp.provenance import unb64, verify_jws, STATEMENT_TYPE

        envelope = self.envelope
        key = self.registry.keys[parse_header(envelope)["kid"]].public_key
        data = {"jws": envelope, "jwk": {"kty": "OKP", "crv": "Ed25519", "x": b64(key.public_bytes_raw())}}
        script = """const c=require('node:crypto');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const d=JSON.parse(s),j=d.jws; const input=Buffer.from(j.protected+'.'+j.payload);const valid=c.verify(null,input,c.createPublicKey({key:d.jwk,format:'jwk'}),Buffer.from(j.signature,'base64url'));const pair=c.generateKeyPairSync('ed25519');const signature=c.sign(null,input,pair.privateKey).toString('base64url');process.stdout.write(JSON.stringify({valid,jwk:pair.publicKey.export({format:'jwk'}),jws:{...j,signature}}));});"""
        output = json.loads(subprocess.check_output(["node", "-e", script], input=json.dumps(data).encode()))
        self.assertTrue(output["valid"])
        other = __import__(
            "cryptography.hazmat.primitives.asymmetric.ed25519", fromlist=["Ed25519PublicKey"]
        ).Ed25519PublicKey.from_public_bytes(unb64(output["jwk"]["x"], 50))
        self.assertEqual(verify_jws(output["jws"], other, STATEMENT_TYPE), unb64(envelope["payload"], 86000))
