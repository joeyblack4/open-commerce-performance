import copy
import http.client
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from ocp.consumer import bootstrap_local, consume, read_local
from ocp.decision import decide
from ocp.model import instant
from ocp.registry import Registry
from ocp.server import create_server

NOW = instant("2026-10-25T20:00:00Z")


class ConsumerHttpTests(unittest.TestCase):
    def setUp(self):
        self.registry = Registry()
        self.server = create_server(0, self.registry, lambda: NOW)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.origin = f"http://127.0.0.1:{self.server.server_port}"
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "trust.json"
        self.pins = bootstrap_local(self.origin, self.path)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def test_consumer_changes_choice_and_can_abstain(self):
        self.assertEqual(
            consume(self.pins, "delivery", now=NOW)["decision"]["choice"], "fictional:merchant-a"
        )
        self.assertEqual(
            consume(self.pins, "price", now=NOW)["decision"]["choice"], "fictional:merchant-unknown"
        )
        self.assertIsNone(consume(self.pins, "tight", now=NOW)["decision"]["choice"])
        base = decide(self.registry.bundle(NOW), "delivery", False)
        self.assertIsNone(base["choice"])

    def test_future_consumer_clock_rejects_expired_fixture(self):
        result = consume(self.pins, "delivery", now=instant("2027-01-01T00:00:00Z"))
        self.assertIsNone(result["decision"]["choice"])
        self.assertFalse(any(row["current"] for row in result["verification_receipts"]))

    def test_consumer_does_not_call_server_verifier_or_decision(self):
        paths = []

        def fetch(path):
            paths.append(path)
            self.assertNotIn("/verification", path)
            self.assertNotIn("/scenarios", path)
            return read_local(self.origin, path)

        result = consume(self.pins, "delivery", fetch=fetch, now=NOW)
        self.assertEqual(result["decision"]["choice"], "fictional:merchant-a")
        self.assertGreater(len(paths), 10)

    def test_offline_tamper_revoke_stale_fail_closed(self):
        for mode in ["tamper", "revoke", "stale"]:
            result = consume(self.pins, "delivery", now=NOW, inject=mode)
            self.assertIsNone(result["decision"]["choice"])
            self.assertFalse(any(x["current"] for x in result["verification_receipts"]))

    def test_untrusted_status_authority_fails(self):
        pins = copy.deepcopy(self.pins)
        pins["status_public_key"] = pins["keys"][0]["x"]
        result = consume(pins, "delivery", now=NOW)
        self.assertIsNone(result["decision"]["choice"])

    def test_pins_not_silently_replaced_and_restart_not_trusted(self):
        with self.assertRaises(FileExistsError):
            bootstrap_local(self.origin, self.path)
        r = Registry()

        def offline(path):
            if path.endswith("/performance"):
                subject = path.split("/")[3]
                return {
                    "subject": subject,
                    "statements": [
                        "/v0/statements/" + i for i, (_, s) in r.ownership.items() if s == subject
                    ],
                }
            identity = path.split("/")[3]
            return r.signed_status(identity, NOW) if path.endswith("/status") else r.envelopes[identity]

        self.assertIsNone(consume(self.pins, "delivery", fetch=offline, now=NOW)["decision"]["choice"])

    def test_withdrawal_even_with_old_etag_is_gone(self):
        identity = next(iter(self.registry.ownership))
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        conn.request("GET", "/v0/statements/" + identity)
        response = conn.getresponse()
        etag = response.getheader("ETag")
        response.read()
        self.registry.withdraw("fixture-a")
        conn.request("GET", "/v0/statements/" + identity, headers={"If-None-Match": etag})
        response = conn.getresponse()
        self.assertEqual(response.status, 410)
        self.assertEqual(response.getheader("Cache-Control"), "no-store")
        response.read()
        conn.close()
        self.assertIsNone(consume(self.pins, "delivery", now=NOW)["decision"]["choice"])

    def test_revoked_key_reported_by_signed_status(self):
        self.registry.revoke_key("fixture-a-ephemeral-1")
        # replay the previously cached envelope: current status still prevents using it
        saved = self.registry.envelopes.copy()

        def fetch(path):
            if path.endswith("/performance"):
                subject = path.split("/")[3]
                return {
                    "subject": subject,
                    "statements": [
                        "/v0/statements/" + i for i, (_, s) in self.registry.ownership.items() if s == subject
                    ],
                }
            identity = path.split("/")[3]
            return self.registry.signed_status(identity, NOW) if path.endswith("/status") else saved[identity]

        self.assertIsNone(consume(self.pins, "delivery", fetch=fetch, now=NOW)["decision"]["choice"])

    def test_host_origin_mutations_and_unknown_protocol(self):
        for method, path, headers, status in [
            ("POST", "/v0/demo", {}, 405),
            ("GET", "/v0/demo", {"Host": "evil.invalid"}, 421),
            ("GET", "/v0/demo", {"Origin": "https://evil.invalid"}, 403),
            ("GET", "/v0/demo?segment=one", {}, 400),
            ("GET", "/.well-known/ucp", {}, 404),
            ("GET", "/v0/statements/other", {}, 404),
            ("GET", "/../pyproject.toml", {}, 400),
        ]:
            conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
            conn.request(method, path, headers=headers)
            response = conn.getresponse()
            self.assertEqual(response.status, status, (method, path))
            response.read()
            conn.close()

    def test_consumer_no_network_outside_loopback(self):
        for origin in [
            "https://merchant.invalid",
            "http://127.0.0.1:8787/other",
            "http://user@127.0.0.1:8787",
        ]:
            with self.assertRaises(ValueError):
                read_local(origin, "/v0/keys")

    def test_policy_refunds_do_not_rank_or_select_by_low_incidence(self):
        bundle = self.registry.bundle(NOW)
        for merchant in bundle["merchants"]:
            for evidence in merchant["evidence"]:
                if evidence["statement"]["metric"]["id"] == "order_refund_incidence":
                    evidence["statement"]["metric"]["value"] = 0
                    evidence["statement"]["refund_policy"]["id"] = "no-refunds"
        self.assertEqual(decide(bundle, "delivery")["choice"], "fictional:merchant-a")

    def test_scope_mismatch_not_comparable(self):
        bundle = self.registry.bundle(NOW)
        # Both meet the preference, but a geography mismatch must not yield a winner.
        for merchant in bundle["merchants"][:2]:
            evidence = merchant["evidence"][0]
            evidence["statement"]["metric"]["value"] = 0.9
        bundle["merchants"][1]["evidence"][0]["statement"]["comparison"]["country"] = "CA"
        self.assertEqual(decide(bundle, "delivery")["state"], "not_comparable")
