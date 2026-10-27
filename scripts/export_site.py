#!/usr/bin/env python3
"""Export the fictional portable preview as static GitHub Pages assets; no source records or private keys."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import shutil
import subprocess

from ocp.contract import ROOT
from ocp.model import instant
from ocp.portable import BUSINESSES, METHODS, PortablePreview
from ocp.provenance import b64

FIXTURE_CLOCK = "2026-10-25T20:00:00Z"


def export(output=None):
    output = Path(output or ROOT / "dist")
    if not (output / "index.html").is_file():
        raise ValueError("Build the hosted frontend before exporting static fixtures")
    proposal = ROOT / "docs/proposal/portable-business-evidence.pdf"
    raw = proposal.read_bytes()
    if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-512:]:
        raise ValueError("A complete proposal PDF is required for publication")
    preview = PortablePreview()
    fixture_dir = output / "fixtures"
    fixture_dir.mkdir(exist_ok=True)
    now = instant(FIXTURE_CLOCK)
    count = 0
    for business, data in BUSINESSES.items():
        for size in range(len(data["metrics"]) + 1):
            for selected in combinations(data["metrics"], size):
                for state in ("published", "withdrawn", "disputed"):
                    for need in data["needs"]:
                        result = preview.preview(business, list(selected), state, need["id"], now)
                        result["static_snapshot"] = True
                        result["checks_recorded_at_fixture_clock"] = FIXTURE_CLOCK
                        filename = "--".join(
                            (business, "_".join(sorted(selected)) or "none", state, need["id"])
                        )
                        (fixture_dir / (filename + ".json")).write_text(json.dumps(result) + "\n")
                        count += 1
    trust = {
        "purpose": "Public fixture keys only. Discovery is not real business identity or source trust.",
        "fixture_clock": FIXTURE_CLOCK,
        "status_public_key": b64(preview.status_key.public_key().public_bytes_raw()),
        "keys": [
            {
                "kid": k.kid,
                "issuer": k.issuer,
                "subject": k.subject,
                "tenant": k.tenant,
                "valid_from": k.valid_from,
                "valid_until": k.valid_until,
                "kty": "OKP",
                "crv": "Ed25519",
                "x": b64(k.public_key.public_bytes_raw()),
            }
            for k in preview.keys.values()
        ],
    }
    (output / "fixture-public-keys.json").write_text(json.dumps(trust, indent=2) + "\n")
    (output / "methods.json").write_text(json.dumps(METHODS, indent=2) + "\n")
    copies = {
        "proposal.pdf": "docs/proposal/portable-business-evidence.pdf",
        "proposal.docx": "docs/proposal/portable-business-evidence.docx",
        "proposal.md": "docs/CEO_BRIEF.md",
        "concept.md": "docs/BUSINESS_DISCOVERY_CONCEPT.md",
        "protocol.md": "docs/PORTABLE_EVIDENCE_PROTOCOL.md",
        "schema.json": "spec/schemas/portable-claim.schema.json",
        "preview.png": "docs/screenshots/portable-desktop.png",
        "LICENSE": "LICENSE",
        "NOTICE": "NOTICE",
        "THIRD_PARTY_NOTICES.md": "THIRD_PARTY_NOTICES.md",
    }
    for destination, source in copies.items():
        shutil.copyfile(ROOT / source, output / destination)
    font_license = ROOT / "node_modules/@fontsource/inter/LICENSE"
    if font_license.is_file():
        shutil.copyfile(font_license, output / "FONT_LICENSE.txt")
    (output / ".nojekyll").write_text("")
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    files = {
        str(p.relative_to(output)): sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "publication.json"
    }
    manifest = {
        "source_commit": commit,
        "synthetic_only": True,
        "fixture_clock": FIXTURE_CLOCK,
        "preview_combinations": count,
        "checks": "Recorded during export; no live source or real-time status service.",
        "files": files,
    }
    (output / "publication.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"source_commit": commit, "preview_combinations": count, "files": len(files)}))
    return manifest


if __name__ == "__main__":
    export()
