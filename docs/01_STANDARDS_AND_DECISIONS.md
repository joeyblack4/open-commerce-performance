# Alignment-first protocol compatibility — mandatory gate

**Verified research snapshot 2026-10-25. This is a STARTING POINT. Codex must refresh upstream directly before building.**

| System | Official purpose | OCP approach | Don't do |
|---|---|---|---|
| UCP (Google + Shopify ecosystem) | Commerce capability discovery, negotiation, checkout/order/catalog and extensions | Primary interoperability investigation. Consider third-party vendor-namespace capability `ai.black4.commerce.performance` only if valid against current schema and namespace authority rules. Otherwise use external evidence profile + proposed upstream convention. | Pretend arbitrary JSON at `/.well-known/ucp` is conformant; replace UCP base/checkout; use unapproved `dev.ucp.*` namespace. |
| OpenAI ACP | ChatGPT product feeds, agentic checkout and delegated payments | Map verified claims to supported product-feed/merchant-signal paths only if official schema admits them; otherwise companion URI and separate public agent endpoint. Submit enhancement separately. | Assume ChatGPT uses OCP or accepts undocumented custom feed fields. |
| Google AP2 | Agent authorization and payment/checkout mandates | Compatible by leaving payments to UCP/ACP/AP2, not treating payment settlement as proof of quality. | Build a new authorization/payment mandate. |
| MCP / A2A | Agent tool transport and agent-to-agent interoperability | Optional read-only client of our evidence service; consistent semantics with REST/JSON. | Invent a competing transport. |
| W3C Verifiable Credentials 2.0 | Portable tamper-evident claims from identifiable issuer | Candidate proof envelope, with issuer trust, provenance and separate empirical verification; evaluate existing supported integrity formats. | Claim signature => truthful underlying metric; create nonconformant pseudo-VCs. |
| JSON Schema 2020-12 | Validation for neutral evidence JSON | Use for OCP's standalone candidate schema. | Claim it is an official UCP extension without negotiation. |

## UCP specifics observed

- Official GitHub organization `Universal-Commerce-Protocol` and repository `ucp`; latest published release indicated as `v2026-08-25` on 2026-10-25. The announcement/release introduces independent capability versioning, vertical refactors, namespace binding and catalog/cart policies. HEAD may evolve independently of release.
- UCP uses capabilities advertised in a merchant profile under `/.well-known/ucp`, reverse-domain names, schema URLs, version constraints, and official discovery/negotiation rules.
- UCP contribution guidance: significant changes need an Enhancement Proposal / council review; start experimental capabilities under a vendor-owned namespace before seeking adoption in `dev.ucp.*`.
- UCP spec uses namespace authority binding. Hosting evidence at `black4.ai` does not by itself grant permission to alter another merchant's `/.well-known/ucp` response. A merchant must explicitly cooperate; possible external profile flow needs maintainer review.

## Proposed decision checkpoints

**ADR-0001 (PENDING):** Native UCP third-party capability vs evidence endpoint linked from merchant-controlled UCP profile vs standalone agent-readable evidence registry. The public external evidence endpoint is the provisional implementation seam, pending upstream validation. It is **not** itself a UCP-defined feature.

**ADR-0002 (PENDING):** Which verifiable credential/signature method is implementable and conformant, how verifier trust is established and how revocation works.

**ADR-0003 (PENDING):** Portable identity model for SKU/GTIN/variant, merchant/physical location and operational channels; avoid product-vendor-merchant conflation.

**ADR-0004 (PENDING):** Whether v0 needs or should defer MCP vs plain HTTPS JSON, and whether embedding evidence into UCP conflicts with normalization rules.

## Acceptance requirements

1. Cite official docs and version/commit; list current open proposals addressing trust, fulfillment or product quality.
2. Evaluate existing UCP `policies[]`, fulfillment and shopping data before introducing new overlapping vocabulary; distinguish PROMISE from OBSERVED OUTCOME.
3. Compare publishability across Shopify, Square and merchant-hosted paths.
4. Implement specification checks that fail loudly on unknown/unsupported UCP versions instead of silently mutating structures.
5. No promise that Shopify, Square, Google or OpenAI will endorse, host, prioritize, or ingest our evidence.

Reference links and access notes: `09_SOURCE_REGISTER.md`.
