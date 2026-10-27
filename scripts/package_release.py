#!/usr/bin/env python3
"""Build a deterministic, allowlisted experimental reference archive from a clean committed HEAD."""

from hashlib import sha256
import json
import re
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    ".github/workflows/pages.yml",
    "CONTRIBUTING.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "AGENTS.md",
    "CODEX_HANDOFF.md",
    "THIRD_PARTY_NOTICES.md",
    "VERIFICATION.md",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "uv.lock",
    "index.html",
    "tsconfig.json",
    "vite.config.js",
    "vitest.config.ts",
    ".gitignore",
}
DIRECTORIES = {"src", "web", "tests", "spec", "examples", "scripts", "docs"}
EXCLUDED = {"node_modules", ".venv", ".git", "artifacts", "__pycache__", ".ruff_cache"}


def allowed(path):
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts or any(part in EXCLUDED for part in pure.parts):
        return False
    if any(
        part.startswith((".env", "secrets", "credentials", "private"))
        or "local-trust" in part
        or part.endswith((".pem", ".key", ".pyc"))
        for part in pure.parts
    ):
        return False
    return path in ROOT_FILES or len(pure.parts) > 1 and pure.parts[0] in DIRECTORIES


def check_content(path, raw):
    if path.endswith(".json"):

        def inspect(value):
            if isinstance(value, dict):
                if value.get("kty") in ("OKP", "EC", "RSA", "oct") and any(
                    k in value for k in ("d", "p", "q", "k")
                ):
                    raise ValueError("private JWK material in review source: " + path)
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)

        inspect(json.loads(raw))
    # Binary images are the exact screenshots captured for the review; no metadata is synthesized.
    if path.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return
    for prefix in [b"/" + b"Users/", b"/" + b"home/", b"/" + b"mnt/data/"]:
        if prefix in raw:
            raise ValueError("machine-local path in review source: " + path)
    if re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----", raw):
        raise ValueError("private key material in review source: " + path)


def build(root=ROOT, output=None):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])

    for args in [("diff", "--quiet"), ("diff", "--cached", "--quiet")]:
        if subprocess.run(["git", "-C", str(root), *args], check=False).returncode:
            raise ValueError("commit the reviewed changes before packaging")
    commit = git("rev-parse", "HEAD").decode().strip()
    entries = []
    for row in git("ls-tree", "-r", "-z", "HEAD").split(b"\0"):
        if not row:
            continue
        metadata, filename = row.split(b"\t", 1)
        path = filename.decode("utf-8")
        if not allowed(path):
            continue
        if metadata.split()[0] not in (b"100644", b"100755"):
            raise ValueError("symlink/submodule cannot enter review archive: " + path)
        raw = git("show", "HEAD:" + path)
        check_content(path, raw)
        entries.append((path, raw, metadata.startswith(b"100755")))
    required = {
        "README.md",
        "LICENSE",
        "NOTICE",
        "docs/SHARE_PACKAGE.md",
        "THIRD_PARTY_NOTICES.md",
        "docs/LICENSE_RECOMMENDATION.md",
        "spec/vendor/ucp/2026-08-25/LICENSE",
    }
    if not required <= {path for path, _, _ in entries}:
        raise ValueError("review package lacks entry point or license notices")
    manifest = {
        "kind": "EXPERIMENTAL REFERENCE SNAPSHOT",
        "commit": commit,
        "synthetic_only": True,
        "public_license": "Apache-2.0; third-party material retains its own notices",
        "files": {path: sha256(raw).hexdigest() for path, raw, _ in sorted(entries)},
    }
    output = output or root / "artifacts/open-commerce-performance-review.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:

        def write(path, raw, executable=False):
            item = zipfile.ZipInfo(
                "open-commerce-performance-review/" + path, date_time=(1980, 1, 1, 0, 0, 0)
            )
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = (0o100755 if executable else 0o100644) << 16
            archive.writestr(item, raw)

        write("REVIEW_MANIFEST.json", (json.dumps(manifest, indent=2) + "\n").encode())
        for path, raw, executable in sorted(entries):
            write(path, raw, executable)
    result = {
        "archive": str(output),
        "commit": commit,
        "files": len(entries),
        "sha256": sha256(output.read_bytes()).hexdigest(),
        "bytes": output.stat().st_size,
    }
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    build()
