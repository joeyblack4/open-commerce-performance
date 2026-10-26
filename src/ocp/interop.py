"""Narrow offline vendor-extension experiment against immutable UCP release schemas.

Not a UCP server or general negotiation implementation. No network schema fetch.
"""

from hashlib import sha256
import json
from urllib.parse import urlsplit
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from .contract import ROOT

UCP = "2026-08-25"
EXT = "ai.black4.commerce.performance"
PARENT = "dev.ucp.shopping.catalog.lookup"
EXT_VERSION = "2026-10-25"
SCHEMA_URL = "https://black4.ai/ocp/unhosted/2026-10-25/catalog-evidence.schema.json"
VENDOR = ROOT / "spec/vendor/ucp" / UCP


def schemas():
    manifest = json.loads((VENDOR / "manifest.json").read_text())
    registry = Registry()
    for path, expected in manifest["files"].items():
        raw = (VENDOR / path).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError("pinned upstream schema changed")
        data = json.loads(raw)
        registry = registry.with_resource(data["$id"], Resource.from_contents(data))
    ext = json.loads((ROOT / "examples/ucp/catalog-evidence.schema.json").read_text())
    registry = registry.with_resource(SCHEMA_URL, Resource.from_contents(ext))
    return registry


def validate_ucp(data, resource, definition=None):
    uri = "https://ucp.dev/schemas/" + resource
    if definition:
        uri += "#/$defs/" + definition
    Draft202012Validator({"$ref": uri}, registry=schemas(), format_checker=FormatChecker()).validate(data)


def authority_bound(name, url):
    """Fixture pre-fetch authority check only. No DNS, redirects, or network fetching here."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.username or parsed.password or not parsed.hostname:
        return False
    try:
        import ipaddress

        ipaddress.ip_address(parsed.hostname)
        return False
    except ValueError:
        pass
    host = parsed.hostname.rstrip(".").lower()
    if len(host.split(".")) < 2:
        return False
    prefix = ".".join(host.split(".")[::-1])
    return name == prefix or name.startswith(prefix + ".")


def profile(opt_in=False):
    capabilities = {
        PARENT: [
            {
                "version": UCP,
                "schema": f"https://ucp.dev/{UCP}/schemas/shopping/catalog_lookup.json",
                "spec": f"https://ucp.dev/{UCP}/specification/shopping/catalog/lookup",
            }
        ]
    }
    if opt_in:
        capabilities[EXT] = [
            {
                "version": EXT_VERSION,
                "extends": PARENT,
                "schema": SCHEMA_URL,
                "spec": "https://black4.ai/ocp/unhosted/2026-10-25/catalog-evidence",
            }
        ]
    return {
        "ucp": {
            "version": UCP,
            "services": {
                "dev.ucp.shopping": [
                    {
                        "version": UCP,
                        "transport": "rest",
                        "endpoint": "https://merchant.example.invalid/ucp/v1",
                        "schema": f"https://ucp.dev/{UCP}/services/shopping/rest.openapi.json",
                        "spec": f"https://ucp.dev/{UCP}/specification/overview",
                    }
                ]
            },
            "capabilities": capabilities,
            "payment_handlers": {},
        }
    }


def fixture_negotiation(business, platform):
    """Only these exact fixture versions/parent supported; never claims full UCP negotiation."""
    for p in (business, platform):
        if p["ucp"]["version"] != UCP:
            raise ValueError("unsupported UCP version; re-audit required")
        validate_ucp(p, "profile.json", "business_schema" if p is business else "platform_schema")
    agreed = {}
    for name, entries in business["ucp"]["capabilities"].items():
        offered = platform["ucp"]["capabilities"].get(name, [])
        for entry in entries:
            if name.startswith("dev.ucp.") and entry["version"] != UCP:
                continue
            if not authority_bound(name, entry["schema"]):
                continue
            for peer in offered:
                if (
                    peer["version"] == entry["version"]
                    and peer["schema"] == entry["schema"]
                    and authority_bound(name, peer["schema"])
                ):
                    if name == PARENT and entry["version"] == UCP:
                        agreed[name] = entry["version"]
                    if (
                        name == EXT
                        and entry["version"] == EXT_VERSION
                        and entry.get("extends") == peer.get("extends") == PARENT
                    ):
                        agreed[name] = entry["version"]
    if PARENT not in agreed:
        agreed.pop(EXT, None)
    return agreed


def catalog():
    price = {"amount": 2400, "currency": "USD"}
    return {
        "ucp": {"version": UCP, "capabilities": {PARENT: [{"version": UCP}]}},
        "products": [
            {
                "id": "fictional-product-box",
                "title": "Fictional grocery box",
                "description": {"plain": "Identical synthetic comparison item."},
                "price_range": {"min": price, "max": price},
                "variants": [
                    {
                        "id": "fictional-variant-box",
                        "title": "Standard box",
                        "description": {"plain": "Synthetic item, not for sale."},
                        "price": price,
                        "inputs": [{"id": "fictional-variant-box", "match": "exact"}],
                    }
                ],
            }
        ],
    }


def catalog_for(negotiated):
    base = catalog()
    if EXT in negotiated:
        base["ucp"]["capabilities"][EXT] = [{"version": EXT_VERSION}]
        base["ocp_evidence"] = [
            {
                "subject_type": "merchant",
                "subject_id": "fictional:merchant-a",
                "uri": "https://merchant.example.invalid/ocp/v0/subjects/fictional:merchant-a/performance",
            }
        ]
    return base


def demonstration():
    business = profile(True)
    unsupported = fixture_negotiation(business, profile(False))
    opted_in = fixture_negotiation(business, profile(True))
    base, extended = catalog_for(unsupported), catalog_for(opted_in)
    validate_ucp(base, "shopping/catalog_lookup.json", "lookup_response")
    Draft202012Validator(
        {"$ref": SCHEMA_URL + "#/$defs/" + PARENT}, registry=schemas(), format_checker=FormatChecker()
    ).validate(extended)
    return {
        "status": "offline_schema_and_fixture_intersection_passed",
        "upstream": {"version": UCP, "sha": "87dd4b1fcff9105d68173120897237fa784c74ef"},
        "business_profile": business,
        "unsupported_agent_catalog": base,
        "opted_in_agent_catalog": extended,
        "unchanged_products": base["products"] == extended["products"],
        "limitations": "Hypothetical HTTPS schema/profile/evidence URLs are UNHOSTED. "
        "No UCP endpoint, live authority/fetch/signature negotiation, checkout or conformance certification. "
        "Actual sidecar retrieval/verification uses the separate explicitly pinned local consumer.",
    }


if __name__ == "__main__":
    print(json.dumps(demonstration(), indent=2))
