import json
import runpy
import unittest
from unittest.mock import patch
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from ocp.contract import ROOT
from ocp.interop import (
    demonstration,
    profile,
    fixture_negotiation,
    catalog_for,
    catalog,
    validate_ucp,
    schemas,
    authority_bound,
    EXT,
    PARENT,
    SCHEMA_URL,
)


class ProtocolTests(unittest.TestCase):
    def test_unmodified_base_and_opt_in_vendor_composition(self):
        result = demonstration()
        self.assertTrue(result["unchanged_products"])
        self.assertNotIn("ocp_evidence", result["unsupported_agent_catalog"])
        self.assertEqual(result["unsupported_agent_catalog"], catalog())
        self.assertIn("ocp_evidence", result["opted_in_agent_catalog"])
        validate_ucp(result["business_profile"], "profile.json", "business_schema")
        validate_ucp(result["opted_in_agent_catalog"], "shopping/catalog_lookup.json", "lookup_response")

    def test_unknown_protocol_rejected_and_exact_versions_intersect(self):
        for version in ["2099-01-01", "2026-04-08"]:
            p = profile(True)
            p["ucp"]["version"] = version
            with self.assertRaises(ValueError):
                fixture_negotiation(profile(True), p)
        p = profile(True)
        p["ucp"]["capabilities"][EXT][0]["version"] = "2026-10-26"
        self.assertNotIn(EXT, fixture_negotiation(profile(True), p))
        p = profile(True)
        del p["ucp"]["capabilities"][PARENT]
        self.assertNotIn(EXT, fixture_negotiation(profile(True), p))
        p = profile(True)
        p["ucp"]["capabilities"][PARENT][0]["version"] = "2026-04-08"
        self.assertNotIn(PARENT, fixture_negotiation(profile(True), p))

    def test_namespace_pre_fetch_binding(self):
        self.assertTrue(authority_bound(EXT, SCHEMA_URL))
        for url in [
            "https://black4.ai.attacker.invalid/schema",
            "https://black4.ai@attacker.invalid/schema",
            "http://black4.ai/schema",
            "https://127.0.0.1/schema",
            "https://localhost/schema",
            "https://cdn.black4.ai/schema",
        ]:
            self.assertFalse(authority_bound(EXT, url))
        self.assertFalse(authority_bound("ai.black4evil.commerce.performance", SCHEMA_URL))
        p = profile(True)
        p["ucp"]["capabilities"][EXT][0]["schema"] = "https://attacker.invalid/schema"
        self.assertNotIn(EXT, fixture_negotiation(p, profile(True)))

    def test_extension_does_not_overload_attribution_or_claim_product_quality(self):
        extended = catalog_for({PARENT: "2026-08-25", EXT: "2026-10-25"})
        extended["ocp_evidence"][0]["subject_type"] = "product_model"
        with self.assertRaises(ValidationError):
            Draft202012Validator(
                {"$ref": SCHEMA_URL + "#/$defs/" + PARENT}, registry=schemas(), format_checker=FormatChecker()
            ).validate(extended)
        self.assertNotIn("attribution", catalog())

    def test_saved_fixture_payloads_validate_offline(self):
        for path, resource, definition in [
            ("business-profile.json", "profile.json", "business_schema"),
            ("catalog-base.json", "shopping/catalog_lookup.json", "lookup_response"),
            ("order-base.json", "shopping/order.json", None),
        ]:
            validate_ucp(json.loads((ROOT / "examples/ucp" / path).read_text()), resource, definition)

    def test_audit_drift_and_failures_are_explicit(self):
        audit = runpy.run_path(str(ROOT / "scripts/protocol_audit"))
        baseline = {"ucp": {"head": "abc", "version": "v2026-08-25"}}
        snapshot = {
            "repositories": [
                {
                    "name": "ucp",
                    "head": {"sha": "abc"},
                    "releases": [{"tag": "v2026-08-25", "prerelease": False}],
                }
            ]
        }
        self.assertEqual(audit["compatibility"](snapshot, baseline), "reviewed_snapshot_unchanged")
        snapshot["repositories"][0]["head"]["sha"] = "new"
        self.assertEqual(audit["compatibility"](snapshot, baseline), "review_required")
        self.assertEqual(audit["compatibility"](snapshot, None), "unreviewed")
        with patch("urllib.request.urlopen", side_effect=OSError("synthetic network failure")):
            # run_path binds urlopen at definition time; explicitly replace its function globals.
            audit["link_audit"].__globals__["urlopen"] = lambda *_args, **_kwargs: (_ for _ in ()).throw(
                OSError()
            )
            result = audit["link_audit"]("https://ucp.dev/")
        self.assertIn("error", result)
