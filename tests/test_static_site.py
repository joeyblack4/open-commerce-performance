from contextlib import redirect_stdout
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

spec = spec_from_file_location("export_site", Path(__file__).parents[1] / "scripts/export_site.py")
site = module_from_spec(spec)
spec.loader.exec_module(site)


class StaticPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        (cls.output / "index.html").write_text("<html>Fictional public demonstration</html>")
        with redirect_stdout(io.StringIO()):
            cls.manifest = site.export(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_every_public_choice_has_a_snapshot_with_explicit_simulated_time(self):
        files = list((self.output / "fixtures").glob("*.json"))
        self.assertEqual(len(files), 72)
        for path in files:
            data = json.loads(path.read_text())
            self.assertTrue(data["static_snapshot"])
            self.assertEqual(data["checks_recorded_at_fixture_clock"], site.FIXTURE_CLOCK)
            self.assertFalse(data["live_registry_changed"])
            if data["state"] != "published" or not data["selected"]:
                self.assertEqual(data["assessment"]["state"], "unknown")

    def test_publication_contains_aggregates_and_public_keys_but_no_source_rows_or_secrets(self):
        for path in (self.output / "fixtures").glob("*.json"):
            raw = path.read_text()
            self.assertNotIn('"rows":', raw)
            self.assertNotIn('"private_key":', raw)
        trust = json.loads((self.output / "fixture-public-keys.json").read_text())
        self.assertEqual(len(trust["keys"]), 3)
        for key in trust["keys"]:
            self.assertIn("x", key)
            self.assertNotIn("d", key)

    def test_pdf_and_every_manifest_digest_match_the_built_publication(self):
        self.assertTrue((self.output / "proposal.pdf").read_bytes().startswith(b"%PDF-"))
        self.assertEqual(self.manifest["preview_combinations"], 72)
        for name, digest in self.manifest["files"].items():
            self.assertEqual(sha256((self.output / name).read_bytes()).hexdigest(), digest)
        self.assertTrue((self.output / "concept.md").is_file())
        self.assertTrue((self.output / "schema.json").is_file())
