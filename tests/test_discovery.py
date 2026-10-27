import copy
import http.client
import json
from threading import Thread
import unittest

from ocp.discovery import discover_businesses
from ocp.model import instant
from ocp.registry import Registry
from ocp.server import create_server

NOW = instant("2026-10-25T20:00:00Z")
PREF = {"max_price": 25, "min_historical_on_time": 0.85}


class BusinessDiscoveryTests(unittest.TestCase):
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
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        conn.request("GET", path)
        response = conn.getresponse()
        result = response.status, response.read()
        conn.close()
        return result

    def test_personal_choice_does_not_create_a_global_business_winner(self):
        delivery = discover_businesses(self.bundle, "shipped-order", PREF)
        price = discover_businesses(self.bundle, "shipped-order", {**PREF, "min_historical_on_time": None})
        self.assertEqual(delivery["decision"]["choice"], "fictional:merchant-a")
        self.assertEqual(price["decision"]["choice"], "fictional:merchant-unknown")
        self.assertEqual(delivery["market_coverage"], "unknown")
        self.assertEqual(delivery["candidates"], price["candidates"])

    def test_unrelated_needs_never_inherit_shipping_history_or_prices(self):
        for context in ("local-pickup", "prepared-meal"):
            for threshold in (None, 0.75, 0.85, 0.95):
                result = discover_businesses(
                    self.bundle, context, {**PREF, "min_historical_on_time": threshold}
                )
                self.assertEqual(result["state"], "scope_not_established")
                self.assertIsNone(result["decision"])
                self.assertEqual(len(result["candidates"]), 3)
                self.assertTrue(all(c["service_fit"] == "not_established" for c in result["candidates"]))

    def test_discovery_never_bypasses_verification_or_mutates_source(self):
        before = copy.deepcopy(self.bundle)
        changed = copy.deepcopy(self.bundle)
        for merchant in changed["merchants"]:
            for evidence in merchant["evidence"]:
                evidence["verification"]["current"] = False
        result = discover_businesses(changed, "shipped-order", PREF)
        self.assertIsNone(result["decision"]["choice"])
        discover_businesses(self.bundle, "local-pickup", PREF)
        self.assertEqual(self.bundle, before)

    def test_unknown_context_and_invalid_preferences_fail_instead_of_widening(self):
        with self.assertRaises(ValueError):
            discover_businesses(self.bundle, "all-businesses", PREF)
        with self.assertRaises(ValueError):
            discover_businesses(self.bundle, "local-pickup", {**PREF, "max_price": 0})

    def test_http_scope_gate_and_exact_query_contract(self):
        query = "budget=2500&priority=price&threshold=85&evidence=on&context=local-pickup"
        code, raw = self.get("/v0/business-discovery?" + query)
        self.assertEqual(code, 200)
        self.assertIsNone(json.loads(raw)["decision"])
        for suffix in ("&context=shipped-order", "&source_cohort=favorable", "&verified=true"):
            self.assertEqual(self.get("/v0/business-discovery?" + query + suffix)[0], 400)
        self.assertEqual(self.get("/v0/business-discovery?" + query.replace("local-pickup", "all"))[0], 400)
        self.assertEqual(self.get("/v0/recommendation?" + query)[0], 400)

    def test_concept_document_served_without_generic_filesystem_access(self):
        code, content = self.get("/concept.md")
        self.assertEqual(code, 200)
        self.assertIn(b"Candidate discovery", content)
        self.assertIn(b"not a global discovery implementation", content)
        self.assertEqual(self.get("/concept.md?path=README.md")[0], 400)
        self.assertEqual(self.get("/docs/BUSINESS_DISCOVERY_CONCEPT.md")[0], 404)
