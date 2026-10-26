from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

spec = spec_from_file_location("package_release", Path(__file__).parents[1] / "scripts/package_release.py")
release = module_from_spec(spec)
spec.loader.exec_module(release)


class ReviewPackageTests(unittest.TestCase):
    def test_export_allowlist_excludes_credentials_dependencies_and_unrelated_files(self):
        for path in [
            ".git/config",
            ".env",
            ".env.production",
            "docs/.env.notes",
            "artifacts/local-trust.json",
            "node_modules/pkg/index.js",
            ".venv/key",
            "src/private.key",
            "src/fixture.pem",
            "../other/README.md",
            "/absolute/file",
            "secrets.json",
            "other/project.md",
        ]:
            self.assertFalse(release.allowed(path), path)
        for path in [
            "README.md",
            "src/ocp/consumer.py",
            "spec/vendor/ucp/2026-08-25/LICENSE",
            "docs/screenshots/shopper.png",
        ]:
            self.assertTrue(release.allowed(path), path)

    def test_machine_paths_and_private_material_are_refused(self):
        for body in [
            b"/" + b"Users/alice/example",
            b"/" + b"home/alice/config",
            b"-----BEGIN " + b"PRIVATE KEY-----\nsynthetic-secret",
        ]:
            with self.assertRaises(ValueError):
                release.check_content("docs/example.md", body)
        release.check_content("README.md", b"Explicitly synthetic local fixture; no credentials.")
        with self.assertRaises(ValueError):
            release.check_content("spec/example.json", b'{"kty":"OKP","d":"synthetic-private"}')
        release.check_content("spec/example.json", b'{"kty":"OKP","x":"synthetic-public"}')

    def test_review_archive_is_deterministic_and_excludes_tracked_environment(self):
        import contextlib
        import io
        import json
        import os
        import subprocess
        import tempfile
        import zipfile

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = [
                "README.md",
                "LICENSE",
                "NOTICE",
                "docs/SHARE_PACKAGE.md",
                "THIRD_PARTY_NOTICES.md",
                "docs/LICENSE_RECOMMENDATION.md",
                "spec/vendor/ucp/2026-08-25/LICENSE",
            ]
            for name in files:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Synthetic review fixture, not production material.\n")
            (root / ".env").write_text("SYNTHETIC_EXCLUDED_VALUE=example\n")
            env = {
                **os.environ,
                "GIT_AUTHOR_NAME": "Fixture",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_NAME": "Fixture",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            }

            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], env=env, check=True, capture_output=True)

            git("init")
            git("add", ".")
            git("commit", "-m", "synthetic export fixture")
            with contextlib.redirect_stdout(io.StringIO()):
                first = release.build(root, root / "first.zip")
                second = release.build(root, root / "second.zip")
            self.assertEqual(first["sha256"], second["sha256"])
            with zipfile.ZipFile(root / "first.zip") as archive:
                self.assertFalse(
                    any(name.endswith("/.env") or "/.git/" in name for name in archive.namelist())
                )
                manifest = json.loads(archive.read("open-commerce-performance-review/REVIEW_MANIFEST.json"))
                self.assertEqual(set(manifest["files"]), set(files))
            (root / "README.md").write_text("uncommitted correction")
            with self.assertRaises(ValueError):
                release.build(root, root / "not-allowed.zip")
