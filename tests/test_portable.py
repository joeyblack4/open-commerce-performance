from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
import http.client
import json
from threading import Thread
import unittest

from ocp.contract import encode
from ocp.model import instant
from ocp.portable import BUSINESSES, METHODS, TYPE, PortablePreview, validate_claim, verify_claim
from ocp.provenance import sign_jws
from ocp.server import create_server

NOW = instant("2026-10-25T20:00:00Z")


class PortableEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.preview = PortablePreview()
        self.methods = {m["id"]: m for m in METHODS.values()}

    def read(self, selected=("pickup",), state="published", business="restaurant", need="pickup"):
        return self.preview.preview(business, list(selected), state, need, NOW)

    def check(self, evidence, now=NOW, subject="fictional:restaurant"):
        return verify_claim(
            evidence["envelope"],
            evidence["signed_status"],
            self.preview.keys["restaurant"],
            self.preview.status_key.public_key(),
            subject,
            self.methods,
            now,
        )

    def test_business_choice_does_not_rewrite_population_or_turn_omission_into_failure(self):
        one = self.read()["evidence"][0]
        both = self.read(("pickup", "net-check"))
        same = next(e for e in both["evidence"] if e["metric"] == "pickup")
        self.assertEqual(one["claim"], same["claim"])
        self.assertEqual(one["claim"]["population"]["eligible_count"], 100)
        self.assertTrue(one["verification"]["usable"])
        self.assertEqual(self.read(())["assessment"]["state"], "unknown")
        self.assertEqual(self.read(("net-check",))["assessment"]["state"], "unknown")
        self.assertEqual(
            self.read(("net-check",), need="net-check")["assessment"]["state"], "supports_consideration"
        )
        self.assertFalse(both["live_registry_changed"])

    def test_all_three_businesses_use_one_envelope_without_provider_endorsement(self):
        for business, data in BUSINESSES.items():
            p = self.read(tuple(data["metrics"]), business=business, need=data["needs"][0]["id"])
            self.assertEqual(len(p["evidence"]), 2)
            for e in p["evidence"]:
                self.assertTrue(e["verification"]["usable"])
                self.assertTrue(e["publisher_reproduced"])
                self.assertFalse(e["claim"]["assurance"]["provider_endorsed"])
            self.assertNotIn('"rows"', json.dumps(p))
            self.assertNotIn('"private_key"', json.dumps(p))

    def test_withdrawal_dispute_expiry_and_identity_mismatch_prevent_use(self):
        for state in ("withdrawn", "disputed"):
            p = self.read(state=state)
            self.assertEqual(p["assessment"]["state"], "unknown")
            self.assertFalse(p["evidence"][0]["verification"]["usable"])
        original = self.read()["evidence"][0]
        self.assertFalse(self.check(original, NOW + timedelta(seconds=61))["usable"])
        self.assertFalse(self.check(original, NOW + timedelta(days=8))["usable"])
        self.assertFalse(self.check(original, subject="fictional:ecommerce")["usable"])

    def test_tampering_claim_or_status_is_rejected(self):
        e = deepcopy(self.read()["evidence"][0])
        e["envelope"]["signature"] = "A" * 86
        self.assertFalse(self.check(e)["usable"])
        e = deepcopy(self.read()["evidence"][0])
        e["signed_status"]["signature"] = "A" * 86
        self.assertFalse(self.check(e)["usable"])

    def test_missing_records_are_unknown_not_zero_and_mean_cannot_hide_them(self):
        self.preview.rows[0]["pickup_minutes"] = None
        p = self.read()
        c = p["evidence"][0]["claim"]
        self.assertIsNone(c["result"]["value"])
        self.assertEqual(c["population"]["missing_count"], 1)
        self.assertEqual(p["assessment"]["state"], "unknown")
        c["result"] = {**c["result"], "value": 14, "state": "observed"}
        with self.assertRaises(ValueError):
            validate_claim(c, self.methods)

    def test_method_digest_unknown_method_and_result_unit_are_checked(self):
        original = self.read()["evidence"][0]["claim"]
        for change in ("digest", "method", "unit", "population"):
            c = deepcopy(original)
            if change == "digest":
                c["method"]["sha256"] = "0" * 64
            elif change == "method":
                c["method"]["id"] = "https://example.invalid/unreviewed-method"
            elif change == "unit":
                c["result"]["unit"] = "people"
            else:
                c["population"]["eligibility"] = "Only the best orders"
            with self.assertRaises(ValueError):
                validate_claim(c, self.methods)
        # The envelope itself accepts a separately versioned new definition; no core KPI enum.
        c = deepcopy(original)
        m = deepcopy(METHODS["pickup"])
        m["id"] = "https://example.invalid/methods/new-industry-method"
        c["method"] = {"id": m["id"], "version": m["version"], "sha256": sha256(encode(m)).hexdigest()}
        validate_claim(c, {m["id"]: m})

    def test_fixture_issuer_cannot_promote_itself_to_provider_or_independent_auditor(self):
        e = deepcopy(self.read()["evidence"][0])
        e["claim"]["assurance"]["provider_endorsed"] = True
        e["envelope"] = sign_jws(
            encode(e["claim"]), self.preview.keys["restaurant"].kid, self.preview.private["restaurant"], TYPE
        )
        result = self.check(e)
        self.assertTrue(result["signature_valid"])
        self.assertFalse(result["usable"])
        self.assertIn("assurance_exceeds_fixture_authority", result["reason"])

    def test_rejects_cross_business_metrics_duplicates_and_unsupported_needs(self):
        for selected in (("response",), ("pickup", "pickup"), ("best-business-score",)):
            with self.assertRaises(ValueError):
                self.read(selected)
        with self.assertRaises(ValueError):
            self.read(need="best")


class PortableHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0, clock=lambda: NOW)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path, method="GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        conn.request(method, path)
        response = conn.getresponse()
        result = response.status, response.read()
        conn.close()
        return result

    def test_exact_read_only_choices_and_public_documents(self):
        query = "/v0/portable-preview?business=restaurant&claims=pickup&state=published&need=pickup"
        code, raw = self.get(query)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["assessment"]["state"], "supports_consideration")
        for extra in ("&cohort=favorable", "&state=published", "&verified=true"):
            self.assertEqual(self.get(query + extra)[0], 400)
        self.assertEqual(self.get(query, "POST")[0], 405)
        for path in ("/brief.md", "/protocol.md", "/v0/portable-schema"):
            self.assertEqual(self.get(path)[0], 200)
            self.assertEqual(self.get(path + "?file=README.md")[0], 400)
