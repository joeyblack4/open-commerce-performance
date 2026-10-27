"""Loopback-only local demo: no deploy configuration, provider proxy, or admin write API."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
from time import monotonic
from urllib.parse import unquote, urlsplit, parse_qs
from .contract import ROOT, encode
from .decision import decide, decide_with_preferences, SCENARIOS
from .preview import merchant_preview
from .interop import demonstration
from .metrics import METHODS
from .model import instant
from .registry import Registry
from .discovery import discover_businesses
from .portable import PortablePreview, METHODS as PORTABLE_METHODS


def create_server(port=8787, registry=None, clock=None):
    registry = registry or Registry()
    portable = PortablePreview()
    clock = clock or (lambda: datetime.now(timezone.utc))
    dist = (ROOT / "dist").resolve()
    requests = []  # one loopback identity; bounded rolling window, local demo only

    class Handler(BaseHTTPRequestHandler):
        server_version = "OCP-Local/0.2.0"

        def log_message(self, *_):
            pass  # no request identifiers in logs

        def answer(self, code, data, content_type="application/json", extra_headers=None):
            body = encode(data) if isinstance(data, (dict, list)) else data
            digest = sha256(body).hexdigest()
            etag = '"' + digest + '"'
            if code == 200 and self.headers.get("If-None-Match") == etag:
                code, body = 304, b""
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for name, value in (extra_headers or {}).items():
                self.send_header(name, value)
            self.send_header("Cache-Control", "no-store")
            self.send_header("ETag", etag)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
            )
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self):
            authority = self.headers.get("Host")
            allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            if authority not in allowed:
                return self.answer(421, {"error": "loopback_host_required"})
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://{x}" for x in allowed}:
                return self.answer(403, {"error": "origin_refused"})
            if len(self.path) > 2000:
                return self.answer(414, {"error": "path_too_long"})
            parsed = urlsplit(self.path)
            if parsed.fragment or (
                parsed.query
                and parsed.path
                not in (
                    "/v0/recommendation",
                    "/v0/merchant-preview",
                    "/v0/business-discovery",
                    "/v0/portable-preview",
                )
            ):
                return self.answer(400, {"error": "arbitrary_segments_and_queries_not_supported"})
            path = unquote(parsed.path)
            if "\\" in path or ".." in path.split("/"):
                return self.answer(400, {"error": "invalid_path"})
            now_m = monotonic()
            while requests and requests[0] < now_m - 60:
                requests.pop(0)
            if len(requests) >= 300:
                return self.answer(429, {"error": "local_read_limit"})
            requests.append(now_m)
            now = clock()
            if path in ("/brief.md", "/protocol.md"):
                name = "CEO_BRIEF.md" if path == "/brief.md" else "PORTABLE_EVIDENCE_PROTOCOL.md"
                return self.answer(200, (ROOT / "docs" / name).read_bytes(), "text/markdown; charset=utf-8")
            if path == "/brief.pdf":
                brief = ROOT / "artifacts/share/portable-business-evidence.pdf"
                if not brief.is_file():
                    return self.answer(404, {"error": "executive_pdf_not_prepared", "text": "/brief.md"})
                return self.answer(200, brief.read_bytes(), "application/pdf")
            if path == "/v0/portable-schema":
                return self.answer(
                    200,
                    (ROOT / "spec/schemas/portable-claim.schema.json").read_bytes(),
                    "application/schema+json",
                )
            if path == "/v0/portable-methods":
                return self.answer(200, {"synthetic": True, "methods": PORTABLE_METHODS})
            if path == "/v0/portable-preview":
                try:
                    query = parse_qs(parsed.query, strict_parsing=True, max_num_fields=4)
                    if set(query) != {"business", "claims", "state", "need"} or any(
                        len(v) != 1 for v in query.values()
                    ):
                        raise ValueError("exact preview choices required")
                    selected = [] if query["claims"][0] == "none" else query["claims"][0].split(",")
                    return self.answer(
                        200,
                        portable.preview(
                            query["business"][0], selected, query["state"][0], query["need"][0], now
                        ),
                    )
                except (ValueError, KeyError):
                    return self.answer(400, {"error": "invalid_portable_preview"})
            if path == "/concept.md":
                return self.answer(
                    200,
                    (ROOT / "docs/BUSINESS_DISCOVERY_CONCEPT.md").read_bytes(),
                    "text/markdown; charset=utf-8",
                )
            if path in ("/v0/recommendation", "/v0/merchant-preview", "/v0/business-discovery"):
                try:
                    query = parse_qs(parsed.query, strict_parsing=True, max_num_fields=6)
                    if any(len(v) != 1 for v in query.values()):
                        raise ValueError("duplicate preference")
                    if path == "/v0/merchant-preview":
                        if set(query) != {"state"}:
                            raise ValueError("exact preview state required")
                        return self.answer(200, merchant_preview(registry, query["state"][0], now))
                    expected = {"budget", "priority", "threshold", "evidence"}
                    if path == "/v0/business-discovery":
                        expected.add("context")
                    if set(query) != expected:
                        raise ValueError("exact shopper preferences required")
                    budget = int(query["budget"][0]) / 100
                    priority = query["priority"][0]
                    if priority not in ("price", "delivery") or query["evidence"][0] not in ("on", "off"):
                        raise ValueError("unknown shopper choice")
                    threshold = int(query["threshold"][0]) / 100
                    if threshold not in (0.75, 0.85, 0.95):
                        raise ValueError("unsupported delivery preference")
                    preference = {
                        "max_price": budget,
                        "min_historical_on_time": threshold if priority == "delivery" else None,
                    }
                    if path == "/v0/business-discovery":
                        return self.answer(
                            200,
                            discover_businesses(
                                registry.bundle(now),
                                query["context"][0],
                                preference,
                                query["evidence"][0] == "on",
                            ),
                        )
                    return self.answer(
                        200,
                        decide_with_preferences(
                            registry.bundle(now), preference, query["evidence"][0] == "on"
                        ),
                    )
                except (ValueError, KeyError, OverflowError):
                    return self.answer(400, {"error": "invalid_preview_or_shopper_preferences"})
            if path == "/v0/interop":
                return self.answer(200, demonstration())
            if path == "/v0/release-info":
                package = ROOT / "artifacts/open-commerce-performance-review.zip"
                return self.answer(
                    200,
                    {
                        "prepared": package.is_file(),
                        "experimental_reference": True,
                        "license": "Apache-2.0",
                        "prepare_command": "npm run package:review",
                    },
                )
            if path == "/v0/release-package":
                package = ROOT / "artifacts/open-commerce-performance-review.zip"
                if not package.is_file():
                    return self.answer(
                        409,
                        {
                            "error": "review_package_not_prepared",
                            "instruction": "Run python scripts/package_release.py from a committed checkout.",
                        },
                    )
                return self.answer(
                    200,
                    package.read_bytes(),
                    "application/zip",
                    {"Content-Disposition": 'attachment; filename="open-commerce-performance-review.zip"'},
                )
            if path == "/v0/scenarios":
                return self.answer(
                    200,
                    {
                        k: {
                            "preference": v,
                            "decision": decide(registry.bundle(now), k),
                            "without_evidence": decide(registry.bundle(now), k, False),
                        }
                        for k, v in SCENARIOS.items()
                    },
                )
            if path == "/v0/demo":
                return self.answer(
                    200, {**registry.bundle(now), "demo_clock": now.isoformat().replace("+00:00", "Z")}
                )
            if path == "/v0/.well-known/ocp":
                return self.answer(
                    200,
                    {
                        "schema_version": "0.2.0",
                        "experimental": True,
                        "synthetic": True,
                        "protocol": "Independent OCP fixture; not UCP, ACP or W3C VC",
                        "subjects": list(x["subject"] for x in registry.bundle(now)["merchants"]),
                        "methods": [f"/v0/methods/{x}/0.2.0" for x in METHODS],
                        "keys": "/v0/keys",
                        "trust": "Ephemeral local keys; pin out of band. Key discovery alone is not trust.",
                    },
                )
            if path == "/v0/schema/0.2.0":
                return self.answer(
                    200,
                    (ROOT / "spec/schemas/performance-statement.schema.json").read_bytes(),
                    "application/schema+json",
                )
            if path == "/v0/keys":
                from .provenance import b64

                return self.answer(
                    200,
                    {
                        "experimental": True,
                        "status_public_key": b64(registry.status_private_key.public_key().public_bytes_raw()),
                        "keys": [
                            {
                                "kid": k.kid,
                                "kty": "OKP",
                                "crv": "Ed25519",
                                "x": b64(k.public_key.public_bytes_raw()),
                                "issuer": k.issuer,
                                "subject": k.subject,
                                "valid_from": k.valid_from,
                                "valid_until": k.valid_until,
                                "revoked": k.revoked,
                            }
                            for k in registry.keys.values()
                        ],
                    },
                )
            parts = path.strip("/").split("/")
            if (
                len(parts) == 4
                and parts[:2] == ["v0", "methods"]
                and parts[2] in METHODS
                and parts[3] == "0.2.0"
            ):
                return self.answer(200, {"version": "0.2.0", "id": parts[2], **METHODS[parts[2]]})
            if len(parts) == 4 and parts[:2] == ["v0", "subjects"] and parts[3] == "performance":
                subject = parts[2]
                if subject not in {s for _, s in registry.ownership.values()}:
                    return self.answer(404, {"error": "not_found"})
                ids = [
                    i
                    for i, (_, s) in registry.ownership.items()
                    if s == subject and registry.get_public(i, now)
                ]
                return self.answer(
                    200,
                    {
                        "subject": subject,
                        "statements": [f"/v0/statements/{i}" for i in ids],
                        "next_page": None,
                        "fixed_bundle": True,
                    },
                )
            if len(parts) in (3, 4) and parts[:2] == ["v0", "statements"]:
                identity = parts[2]
                if identity not in registry.ownership:
                    return self.answer(404, {"error": "not_found"})
                sub = parts[3] if len(parts) == 4 else ""
                if sub == "status":
                    return self.answer(200, registry.signed_status(identity, now))
                if sub == "verification":
                    return self.answer(200, registry.verification(identity, now))
                if sub not in ("", "signature"):
                    return self.answer(404, {"error": "not_found"})
                public = registry.get_public(identity, now)
                if public is None:
                    return self.answer(
                        410,
                        {
                            "statement_id": identity,
                            "state": "not_current",
                            "reason": registry.verification(identity, now)["reason"],
                        },
                    )
                return self.answer(200, public["envelope"] if sub == "signature" else public["statement"])
            if path.startswith("/v0/") or path == "/.well-known/ucp":
                return self.answer(404, {"error": "not_an_implemented_protocol_route"})
            asset = dist / ("index.html" if path == "/" else path.lstrip("/"))
            if not asset.resolve().is_relative_to(dist) or not asset.is_file():
                return self.answer(404, {"error": "demo_assets_missing_run_npm_build"})
            return self.answer(
                200, asset.read_bytes(), mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
            )

        do_HEAD = do_GET

        def do_POST(self):
            self.close_connection = True
            self.answer(405, {"error": "read_only_fixture_demo"})

        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST
        do_OPTIONS = do_POST

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument(
        "--fixture-as-of",
        default="2026-10-25T20:00:00Z",
        help="Explicit synthetic clock; never production freshness",
    )
    parser.add_argument(
        "--real-clock", action="store_true", help="Use real current time, including expiry enforcement"
    )
    args = parser.parse_args()
    frozen = instant(args.fixture_as_of)
    server = create_server(args.port, clock=None if args.real_clock else lambda: frozen)
    print(
        "Clock: real UTC" if args.real_clock else "SYNTHETIC FIXTURE CLOCK: " + args.fixture_as_of, flush=True
    )
    print(f"Synthetic OCP demo: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
