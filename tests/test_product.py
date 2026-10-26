import copy
import http.client
import json
from threading import Thread
import unittest
from ocp.consumer import consume
from ocp.decision import decide_with_preferences
from ocp.model import instant
from ocp.preview import merchant_preview
from ocp.registry import Registry
from ocp.server import create_server
from ocp.provenance import b64

NOW = instant("2026-10-25T20:00:00Z")


class ProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry()
        cls.bundle = cls.registry.bundle(NOW)
        cls.server = create_server(0, cls.registry, lambda: NOW)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        connection.request("GET", path)
        response = connection.getresponse()
        result = (response.status, json.loads(response.read()))
        connection.close()
        return result

    def test_budget_and_history_controls_change_actual_choice(self):
        cases = [
            (25, 0.85, "fictional:merchant-a"),
            (25, 0.75, "fictional:merchant-b"),
            (25, 0.95, None),
            (19, 0.85, None),
            (19, None, "fictional:merchant-unknown"),
        ]
        for budget, threshold, expected in cases:
            result = decide_with_preferences(
                self.bundle, {"max_price": budget, "min_historical_on_time": threshold}
            )
            self.assertEqual(result["choice"], expected)
        self.assertEqual(
            decide_with_preferences(self.bundle, {"max_price": 15, "min_historical_on_time": None})["state"],
            "no_eligible_offers",
        )

    def test_all_192_preference_combinations_match_fixture_expectations(self):
        for budget in range(15, 31):
            for priority in ("price", "delivery"):
                for threshold in (0.75, 0.85, 0.95):
                    for enabled in (True, False):
                        expected = None
                        if priority == "price" and budget >= 18:
                            expected = "fictional:merchant-unknown"
                        elif priority == "delivery" and enabled:
                            if threshold == 0.75 and budget >= 20:
                                expected = "fictional:merchant-b"
                            elif threshold == 0.85 and budget >= 24:
                                expected = "fictional:merchant-a"
                        preference = {
                            "max_price": budget,
                            "min_historical_on_time": threshold if priority == "delivery" else None,
                        }
                        result = decide_with_preferences(self.bundle, preference, enabled)
                        self.assertEqual(result["choice"], expected, (budget, priority, threshold, enabled))

    def test_every_adjustment_resolves_its_stated_preferences(self):
        for budget in range(15, 31):
            for threshold in (0.75, 0.85, 0.95):
                preference = {"max_price": budget, "min_historical_on_time": threshold}
                result = decide_with_preferences(self.bundle, preference)
                for action in result["adjustments"]:
                    adjusted = {
                        "max_price": action["budget"],
                        "min_historical_on_time": action["threshold"] / 100
                        if action["priority"] == "delivery"
                        else None,
                    }
                    self.assertIsNotNone(
                        decide_with_preferences(self.bundle, adjusted, action["evidence"])["choice"],
                        (preference, action),
                    )
        strict = decide_with_preferences(self.bundle, {"max_price": 20, "min_historical_on_time": 0.95})
        self.assertTrue(all(a["threshold"] < 95 or a["priority"] == "price" for a in strict["adjustments"]))
        low_price = decide_with_preferences(self.bundle, {"max_price": 15, "min_historical_on_time": None})
        self.assertEqual(low_price["adjustments"][0]["budget"], 18)

    def test_invalid_preferences_never_widen_to_all_merchants(self):
        for budget in [True, 0, 14.99, 30.01, float("nan"), float("inf"), "25"]:
            with self.assertRaises(ValueError):
                decide_with_preferences(self.bundle, {"max_price": budget, "min_historical_on_time": 0.85})
        for threshold in [0, 0.99, "85", True]:
            with self.assertRaises(ValueError):
                decide_with_preferences(self.bundle, {"max_price": 25, "min_historical_on_time": threshold})
        self.assertEqual(
            decide_with_preferences(self.bundle, {"max_price": 20.01, "min_historical_on_time": 0.75})[
                "choice"
            ],
            "fictional:merchant-b",
        )

    def test_preview_states_use_actual_status_and_preserve_live_registry(self):
        before_consent = dict(self.registry.consent)
        before_lifecycle = copy.deepcopy(self.registry.lifecycle)
        shared = merchant_preview(self.registry, "shared", NOW)
        withdrawn = merchant_preview(self.registry, "withdrawn", NOW)
        disputed = merchant_preview(self.registry, "disputed", NOW)
        self.assertEqual(len(shared["merchant"]["evidence"]), 3)
        for preview in (withdrawn, disputed):
            self.assertEqual(preview["merchant"]["evidence"], [])
            self.assertTrue(all(v["signature_valid"] and not v["current"] for v in preview["status_checks"]))
            self.assertFalse(preview["live_registry_changed"])
            self.assertEqual(len(preview["categories"]), 5)
        self.assertEqual(before_consent, self.registry.consent)
        self.assertEqual(before_lifecycle, self.registry.lifecycle)
        self.assertEqual(len(merchant_preview(self.registry, "shared", NOW)["merchant"]["evidence"]), 3)
        with self.assertRaises(ValueError):
            merchant_preview(self.registry, "hide-refunds", NOW)

    def test_http_preferences_are_bounded_read_only_controls(self):
        status, result = self.get("/v0/recommendation?budget=2500&priority=delivery&threshold=85&evidence=on")
        self.assertEqual((status, result["choice"]), (200, "fictional:merchant-a"))
        status, result = self.get("/v0/recommendation?budget=2500&priority=delivery&threshold=75&evidence=on")
        self.assertEqual((status, result["choice"]), (200, "fictional:merchant-b"))
        for query in [
            "budget=2500&budget=3000&priority=delivery&threshold=85&evidence=on",
            "budget=999999&priority=delivery&threshold=85&evidence=on",
            "budget=2500&priority=delivery&threshold=85&evidence=on&verification=true",
            "budget=2500&priority=delivery&threshold=99&evidence=on",
            "budget=2500&priority=delivery&threshold=85&evidence=on&segment=only-successes",
        ]:
            self.assertEqual(self.get("/v0/recommendation?" + query)[0], 400)
        for state in ["shared", "withdrawn", "disputed"]:
            status, preview = self.get("/v0/merchant-preview?state=" + state)
            self.assertEqual(status, 200)
            self.assertTrue(preview["preview_only"])
        self.assertEqual(self.get("/v0/merchant-preview?state=shared&metric=only-favorable")[0], 400)
        self.assertEqual(self.get("/v0/merchant-preview?state=publish-real")[0], 400)

    def test_client_cannot_inject_usable_evidence(self):
        # The only HTTP inputs are preferences; verification is derived from server-owned signed records.
        broken = Registry()
        broken.envelopes[next(iter(broken.envelopes))]["signature"] = b64(b"\0" * 64)
        result = decide_with_preferences(
            broken.bundle(NOW), {"max_price": 25, "min_historical_on_time": 0.85}
        )
        self.assertIsNone(result["choice"])

    def test_custom_consumer_and_server_share_policy(self):
        r = self.registry
        pins = {
            "origin": "http://127.0.0.1",
            "assumption": "test-pinned fixture",
            "status_public_key": b64(r.status_private_key.public_key().public_bytes_raw()),
            "bindings": {subject: tenant for tenant, subject in r.ownership.values()},
            "keys": [
                {
                    "kid": k.kid,
                    "issuer": k.issuer,
                    "subject": k.subject,
                    "x": b64(k.public_key.public_bytes_raw()),
                    "valid_from": k.valid_from,
                    "valid_until": k.valid_until,
                    "revoked": k.revoked,
                }
                for k in r.keys.values()
            ],
        }

        def fetch(path):
            return self.get(path)[1]

        for budget, threshold in [(25, 0.75), (25, 0.85), (19, None), (19, 0.85)]:
            preference = {"max_price": budget, "min_historical_on_time": threshold}
            independent = consume(pins, "delivery", fetch=fetch, now=NOW, preferences=preference)["decision"]
            expected = decide_with_preferences(r.bundle(NOW), preference)
            self.assertEqual(independent["choice"], expected["choice"])
