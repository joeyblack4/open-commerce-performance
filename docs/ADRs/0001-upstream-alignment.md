# ADR 0001: independent opt-in aggregate evidence

Checked: **2026-10-25, America/Los_Angeles**. Decision: accepted for local synthetic implementation; human standards review remains open. No upstream endorsement or protocol conformance is claimed. Research preceded core implementation.

## Decision

Implement a standalone, opt-in evidence resource and local registry demonstration in Black 4's `open-commerce-performance` repository (initially private; public Apache-2.0 distribution authorized October 26, 2026). It has its own experimental JSON Schema and ordinary HTTP GETs. Final signing uses protected flattened JWS with Ed25519 through joserfc; see [ADR 0002](0002-jws-profile.md). The loopback server does not serve `/.well-known/ucp`, modify ACP feeds/checkout or label JWS a W3C credential. A later offline experiment validates a hypothetical vendor profile/composed catalog against pinned schemas; it does not advertise a live capability. Consumers explicitly opt into reading it. No universal score, affiliate influence or payment/checkout implementation.

Retail Edge is the read-only integration reference. Its Platform Control owns business identity, permissions, consent/review and receipts; Connector Hub owns provider execution; MDW owns tenant evidence. This repository owns reusable methods and synthetic reference code, not another platform. A future real integration must use those owners and their MCP operation registry. See [integration boundary](../ARCHITECTURE.md).

## Exact upstream observations

Authenticated `gh api`, official websites, checked-out source, release-vs-HEAD diff and contribution guides were inspected. [Machine audit](../upstream/2026-10-25.json) records link content hashes, GitHub responses, failures and open-search scope. GitHub tags mean peeled commit SHA, not annotated tag-object SHA. HEAD is development and is not synonymous with published release.

| Source | Published version / commit | Observed HEAD | Meaning for OCP |
|---|---|---|---|
| [UCP](https://github.com/Universal-Commerce-Protocol/ucp/releases/tag/v2026-08-25) | `v2026-08-25` / `87dd4b1fcff9105d68173120897237fa784c74ef` | `ba9795a6a1c55dc98ec50032cc124a77fba16750` | Discovery, negotiation, catalog, cart, checkout, order, policy and fulfillment. Independent component versions; snapshot and HEAD differ. |
| [UCP JS SDK](https://github.com/Universal-Commerce-Protocol/js-sdk/releases/tag/v0.5.1) | `v0.5.1` / `688b6276f4fc90899da265745cef19fec917b24a` | `6f7a6da79739a2ccf868953ed5138f85fb2b6ce3` | SDK `0.5.x` targets UCP `2026-08-25`; generated types/Zod validators, not proof of a new extension's adoption. |
| [UCP Python SDK](https://github.com/Universal-Commerce-Protocol/python-sdk/releases/tag/v2026-08-25) | `v2026-08-25` / `b6f9b91c018f748a92166266004c8b625142cdfb` | `eea5af1f7e569fe0fab1d179ed0786be289bef6f` | Generated schema models; not imported because no transaction payload is implemented. |
| [UCP conformance](https://github.com/Universal-Commerce-Protocol/conformance/tree/016ecbc22240affdec4429a60d539bedd04ab51b) | No tags/releases observed | `016ecbc22240affdec4429a60d539bedd04ab51b` | Tests need seeded merchant checkout/order server; README example targets `2026-04-08`. Not run against an evidence-only endpoint and not represented as certification. |
| [ACP](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/tree/7fdd78df677a94dce04c770644b0fbbb1401272b/spec/2026-04-17) | Dated spec `2026-04-17`; no GitHub tags/releases observed | `7fdd78df677a94dce04c770644b0fbbb1401272b` | Beta interaction model; OpenAPI/JSON Schema snapshots, feed/orders/authentication/MCP. `spec/unreleased` is distinct. OpenAI deployed feed docs are a separate integration contract. |
| [AP2](https://github.com/google-agentic-commerce/AP2/releases/tag/v0.2.0) | `v0.2.0` / `b4587ac1d055888a73b4b21750973cffba961793` | `e1ea56db72a6385bce3e5c1112b3a56ce60acb43` | Checkout/payment mandates, authorization and accountability, not merchant performance. No payment scope here. |
| [MCP](https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28) | `2026-07-28` / `5f5440bb26a62e2cf3440b92da5a667efa03b267` | `dae694f61a31f7a3ec2af3aff709e11f70f61e48` | Optional tool transport, JSON-RPC and per-request negotiation. Plain GET suffices locally. No hand-registered Platform Control tool. |
| [A2A](https://github.com/a2aproject/A2A/releases/tag/v1.0.1) | `v1.0.1` / `3303592588e388e62e0f69f701af531d2f4e3991` | `98279d62316361ba8451eaef300f72b72e169185` | Agent interaction and tasks; does not define this evidence's meaning. No new agent runtime. |
| [W3C VC DM 2.0](https://www.w3.org/TR/2025/REC-vc-data-model-2.0-20250515/) | Recommendation, 2025-05-15 (dated normative publication, not GitHub release) | `w3c/vc-data-model` `8838afd011a17758a225cfb742275592b82c53df` | Data model includes context/type/issuer/subject, validity/status and securing mechanisms. Editor HEAD is not Recommendation. |
| [VC Data Integrity 1.0](https://www.w3.org/TR/2025/REC-vc-data-integrity-20250515/) | Recommendation, 2025-05-15 | Not used as runtime | Cryptosuite, proof purpose, controller/key resolution, canonicalization and status interoperability require a separately tested profile. Deferred; JWS by itself is not a VC profile. |
| [JSON Schema](https://json-schema.org/draft/2020-12) | Draft 2020-12, updated publication 2022-06-16 | Not a protocol integration | Used for this independent schema, with format assertions and semantic validation. |

### UCP released vs HEAD details

The inspected diff from the immutable `v2026-08-25` commit to HEAD touches 105 files, including return-policy and lodging/ask work, namespace guidance and signatures. Pin published versions for any future integration and re-audit maintained release branches separately; a dated tag alone does not establish what a live merchant implements. Current [versioning](https://github.com/Universal-Commerce-Protocol/ucp/blob/ba9795a6a1c55dc98ec50032cc124a77fba16750/docs/versioning.md) describes long-lived release branches and governed backports.

[Namespace authority binding](https://github.com/Universal-Commerce-Protocol/ucp/blob/ba9795a6a1c55dc98ec50032cc124a77fba16750/docs/specification/overview/index.md#authority-binding) binds a capability's HTTPS schema host to its reverse-domain name on label boundaries, without redirects; authority provenance is explicitly not trust. `ai.black4.commerce.performance` would require a matching controlled schema origin and implemented service/capability/version negotiation, not merely a JSON document. Merchant-controlled discovery changes need merchant authorization. No declaration is emitted by a live endpoint. examples/ucp/business-profile.json contains a hypothetical unhosted declaration for offline validation.

Existing [`policies`](https://github.com/Universal-Commerce-Protocol/ucp/blob/87dd4b1fcff9105d68173120897237fa784c74ef/source/schemas/common/types/policy.json) describe durable purchase terms, not historical aggregate outcomes. Existing [fulfillment events](https://github.com/Universal-Commerce-Protocol/ucp/blob/87dd4b1fcff9105d68173120897237fa784c74ef/source/schemas/shopping/types/fulfillment_event.json) distinguish shipped and delivered with line-item quantities; a record labelled delivered is not independently authenticated carrier evidence. Reuse those transaction semantics if source coverage later permits. Do not overload policy URLs or review ratings with refund incidence.

### Governance and overlapping proposals

[UCP contributing](https://ucp.dev/documentation/contributing/) requires an EP and Domain Tech Council approval for major changes; vendor namespaces precede possible core adoption, and breaking changes require Governing Council approval and notice. An upstream proposal is not approval.

Open work inspected (2026-10-25):

- [UCP #836 Correspondence](https://github.com/Universal-Commerce-Protocol/ucp/pull/836): record-to-record comparisons, issuer and observed time, `unverifiable`, field pointers. Direct overlap with lineage and discrepancy semantics; reuse if adopted rather than invent transaction-level equivalents.
- [UCP #837 adjustment cause](https://github.com/Universal-Commerce-Protocol/ucp/pull/837): fulfillment mismatch, terms failures, attribution and scope; useful prospective evidence input, explicitly assertions rather than liability adjudication.
- [UCP #835 agent behavior signals](https://github.com/Universal-Commerce-Protocol/ucp/pull/835), [#630 authentication signals](https://github.com/Universal-Commerce-Protocol/ucp/issues/630), [#797 fraud signals](https://github.com/Universal-Commerce-Protocol/ucp/issues/797): transaction security/risk rather than seller outcome aggregates. Absence should not be scored as risk.
- [UCP #385 product fitment](https://github.com/Universal-Commerce-Protocol/ucp/issues/385): product suitability; avoid conflating it with merchant fulfillment.
- [ACP #221 performance fields](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/issues/221): open question about removed fields, not authorization to restore `return_rate` or `popularity_score`. Current [OpenAI feed reference](https://developers.openai.com/commerce/specs/feed) supports scoped product/store review data and returns metadata; no documented OCP aggregate/attestation ingestion route was established.
- [AP2 #290 post-checkout action record](https://github.com/google-agentic-commerce/AP2/issues/290), [#224 proof of delivery](https://github.com/google-agentic-commerce/AP2/issues/224), [#352 dispute sample](https://github.com/google-agentic-commerce/AP2/pull/352): relevant evidence boundary, payments outside scope.

Search covered open issues and PRs for trust, reputation, performance, quality, evidence and correspondence. It is bounded, not proof no other proposal exists. [ACP governance](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/7fdd78df677a94dce04c770644b0fbbb1401272b/docs/governance.md) uses OpenAI/Stripe founding maintainers, SEPs and CLA; [extension RFC](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/7fdd78df677a94dce04c770644b0fbbb1401272b/rfcs/rfc.extensions.md) is not automatic acceptance of arbitrary feed fields. ACP's validation scripts check schemas/examples/OpenAPI consistency. AP2's [contribution guide](https://github.com/google-agentic-commerce/AP2/blob/e1ea56db72a6385bce3e5c1112b3a56ce60acb43/CONTRIBUTING.md) says the core spec was donated to FIDO, with this repository accepting SDK/sample work; [FIDO announcement](https://fidoalliance.org/fido-alliance-to-develop-standards-for-trusted-ai-agent-interactions/) must be consulted before any core proposal. SDK tests/samples do not certify outcome evidence.

## Alternatives

| Mechanism | Potential merit | Current constraint | Decision |
|---|---|---|---|
| UCP namespaced capability | Discoverable, negotiated service with schema authority | Requires real schema/service/version implementation, host authority, cooperating merchants/clients and upstream fit review | Offline vendor experiment implemented after guidance below; live hosting deferred |
| External resource from supported profile/reference | Could retain native discovery and independent evidence | Open profile fields or generic URLs do not establish a recognized performance link relation or client ingestion | Defer until supported semantics and exact release conformance established |
| Independent opt-in evidence resource | No transaction/profile mutations; portable aggregate and verifier | Distribution and third-party trust unresolved; no automatic ChatGPT visibility | **Choose for local prototype** |

## Signature choice and upstream questions

Use flattened JWS through joserfc (ADR 0002), protecting headers and exact UTF-8 payload in the RFC 7515 signing input; verify those bytes before parsing semantics. No home-grown cross-language JSON canonicalization or W3C-looking `@context`/`proof` fields. Pin issuer trust out of band and bind keys to subject/tenant, issuance validity and current status. Rotation preserves prior keys through statement expiry; compromise revokes all affected evidence immediately. Signature, calculation reproducibility, source authenticity and audit remain separate results.

Before any external step, ask maintainers whether aggregate evidence belongs outside UCP; whether there is a supported link relation; how #836/#837 affect lineage; and whether a vendor capability adds value beyond optional HTTPS retrieval. Ask ACP maintainers about accepted enrichment channels separately. No submission, outreach or external statement hosting is authorized by this ADR.

## Audit behavior

`./scripts/protocol_audit` writes a timestamped snapshot, exits 2 for incomplete network checks and 3 for baseline drift requiring review. It never silently calls an unknown version compatible. Documentation fetch redirects are recorded, not treated as protocol-profile fetch behavior. Rerun before any integration change. Successful audit means observed sources, not protocol conformance.

## Session follow-up: concrete vendor experiment

After the independent resource worked, reviewed [the October 16 contributor response on #185](https://github.com/Universal-Commerce-Protocol/ucp/issues/185#issuecomment-6213400329) and [Shopify engineering](https://shopify.engineering/UCP). They support self-hosted vendor namespaces without TC ratification of the vendor extension; core adoption remains governed. The individual is a CONTRIBUTOR, not formal council approval. Their composition warning matters: allOf intersects constraints, and structured evidence must not overload the flat-string attribution map.

Implemented an offline extension over released dev.ucp.shopping.catalog.lookup, named ai.black4.commerce.performance, exact independent version 2026-10-25, parent $defs mapping, release-pinned requires, namespace-bound hypothetical schema URL and distinct ocp_evidence reference field. Both profiles validate against immutable upstream schemas; base catalog/order remains valid; unsupported clients get unchanged base catalog. Tests reject unknown protocol, mismatched parent/extension versions, wrong authority and product-subject conflation. Fixture intersection is not a full UCP negotiator.

URLs are explicitly UNHOSTED. No DNS/authority proof, HTTPS schema fetch, real discovery or live conformance is implemented. The separate consumer retrieves sidecar evidence only through explicitly pinned loopback trust. This is a concrete UCP extensibility experiment, not adoption or deployment. ACP remains unchanged.

## Adjacent ecosystem refresh for the review package

Checked again on 2026-10-25: [UCP's official announcements](https://ucp.dev/documentation/announcements/) record the July 16 formation of its Food Technical Council with Block (Square), DoorDash, Google, Toast and Uber Eats. Square is therefore a verified participant in that UCP domain, not merely a speculative audience. This does not establish OCP adoption, access to merchant data, or applicability of shipped-grocery aggregate methods to restaurant/local-food service.

[Poppy / Personal Agent Protocol](https://personalagentprotocol.org/docs/spec) is adjacent and **deferred**. The official deployed docs were observed redirecting to `/docs/0.3/spec`, labelled Draft 0.3; breaking changes remain possible before 1.0. Canonical public repository `personal-agent-protocol/personal-agent-protocol` was observed at HEAD `39b35bdf240fc07f157d6ca4e29b5a41d4b36b5d` (2026-10-19), without tags/releases. Its `content/versions/versions.json` lists 0.2 and frozen 0.1. These are discrepant source/deployment observations, not evidence that repository HEAD is a released 0.3 artifact. The audit records both official URLs and repository metadata rather than silently equating them.

[Sierra's October 6 announcement](https://sierra.ai/blog/introducing-personal-agent-protocol) describes personal-agent/company interaction, discovery, authorization/session and existing API/web/conversation access. OCP should supply optional scoped aggregate evidence beside those mechanisms; it must not recreate their discovery/auth/session responsibilities. No Poppy runtime integration or conformance is claimed.

The [W3C/GS1 ecommerce-agent workshop agenda](https://www.w3.org/2026/ecommerce-agents/agenda.html) includes publisher/agent identity and trust discussions. Workshop positions and agenda items are not adopted W3C standards. The verified VC Recommendations and OCP's explicit non-VC JWS profile remain separate.

## Publication refresh — October 26, 2026

The [fresh audit](../upstream/2026-10-26-publication.json) completed network checks and correctly flagged UCP HEAD drift. Reviewed the [four-commit comparison](https://github.com/Universal-Commerce-Protocol/ucp/compare/ba9795a6a1c55dc98ec50032cc124a77fba16750...69895b84b451925a92ac0c9122353eab310e1a23): dependency updates (Pillow/Python minimum, Black and certifi) and an RFC 9421 section-citation correction. The signature requirement is unchanged; no schema files changed. Published UCP remains v2026-08-25, and the reference continues to use its immutable schemas. ACP and AP2 baselines were unchanged. Accepted the new development HEAD in the audit baseline after review; no implementation or conformance claim changed.

## Business discovery revision — October 26, 2026

The current [concept paper](../BUSINESS_DISCOVERY_CONCEPT.md) separates candidate discovery, protocol capability discovery and consumer-specific business suitability. The merchant is the comparison subject; the identical basket is a controlled context. Brand, branch and seller identity cannot be conflated, and broader relationships are not implemented.

Fresh audit `2026-10-26-business-discovery.json` completed with the accepted baseline unchanged. Read the current UCP overview, core concepts, location search/lookup and contribution guidance. The immutable v2026-08-25 tree also contains location schemas/specifications. Location capabilities discover locations from a business; they are not treated here as a global competing-business performance directory. The existing catalog extension is one tested attachment point, not a decision that every business claim belongs under product lookup.

A business-first resource/capability and a location-specific reference are design options for further standards review, not new emitted UCP declarations. No official profile/schema was changed and no new link relation was represented as standard. The standalone local `/v0/business-discovery` is explicitly a seeded synthetic scope experiment, not UCP discovery. It reuses the existing verified decision policy and rejects pickup/meal suitability inference from shipped-order fixtures.
