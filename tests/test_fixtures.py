import unittest
from jsonschema.exceptions import ValidationError
from ocp.contract import ROOT, parse_statement


class FixtureTests(unittest.TestCase):
    def test_positive_fixtures(self):
        files = list((ROOT / "spec/examples").glob("*.json"))
        self.assertGreaterEqual(len(files), 5)
        for path in files:
            self.assertTrue(parse_statement(path.read_bytes())["synthetic"])

    def test_negative_fixtures(self):
        files = list((ROOT / "spec/invalid").glob("*.json"))
        self.assertGreaterEqual(len(files), 5)
        for path in files:
            with self.assertRaises((ValueError, ValidationError), msg=path.name):
                parse_statement(path.read_bytes())
