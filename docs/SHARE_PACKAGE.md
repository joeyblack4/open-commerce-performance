# Portable business evidence sharing package

Start with the [PDF proposal](https://joeyblack4.github.io/open-commerce-performance/proposal.pdf), [public demo](https://joeyblack4.github.io/open-commerce-performance/) and [CEO brief source](CEO_BRIEF.md). It asks source providers and AI platforms to help define a common format for optional business evidence and test it across independent implementations. [Prepared email copy](CEO_OUTREACH.md) accompanies it. No outreach has been sent.

## The message

Portable evidence about a business that an agent can consult during discovery and selection. Businesses choose what to publish. An identified issuer attests to a defined result. The agent decides its relevance to the buyer. Metric definitions remain open; scope and provenance are explicit.

## The working demonstration

Open the public demo with no installation, or run the [local quickstart](../README.md). The landing view has one flow, across three fictional businesses:

- **Restaurant:** select pickup preparation time or average net check. The latter is per check, never per person.
- **Ecommerce:** select delivery by original promise or average dispatch time. The generated source explicitly supplies the required observations; no commerce API is claimed to supply them universally.
- **B2B services:** select first human support response or invoices within accepted fixed-scope quotes.

Choose either measure, both or neither. Change the buyer need. A selected but irrelevant claim does not satisfy a different requirement. Missing, expired, withdrawn and disputed evidence cannot support the assessment. Inspect the exact signed claim and its status in the evidence dialog. Private source rows and keys never appear in the response.

The hosted version replays 72 precomputed, signed publication and buyer-need examples. Its checks were recorded at the explicitly simulated October 25 clock. It runs no Python server, live provider integration or mutable publication service. The local version calculates and checks the examples in process. Both are read-only previews. The claim issuer, source records and business identities are fictional. Signature and status checks use real cryptography with explicit local trust; source accuracy and independent audit remain unestablished. The explanation is a deterministic example, not an LLM call, market search or measured consumer benefit.

## The proposed standard

Read the [concept](BUSINESS_DISCOVERY_CONCEPT.md), [protocol](PORTABLE_EVIDENCE_PROTOCOL.md) and [candidate schema](../spec/schemas/portable-claim.schema.json). Provider, business and industry methods can evolve independently. Shared definitions enable comparisons; the protocol imposes no universal KPI list or business score.

The 0.3 candidate is separate from the earlier 0.2 closed fixture contract, which remains tested. The old fixed bundle is retained only as a technical reference. Standard signing is reused. Neither profile claims W3C VC conformance.

## Existing commerce protocols

The evidence is independently retrievable before purchase and can be referenced by discovery surfaces or supported protocol integrations. UCP catalog, checkout and order responsibilities stay with UCP. The existing catalog-extension fixture passes against immutable released v2026-08-25 schemas; it is offline, with unhosted example URLs. No live negotiation, official adoption or ingestion by an AI platform is claimed.

The [October 27 audit](upstream/2026-10-27-portable-evidence.json) completed network checks and detected UCP development drift. Review found changes in documentation rendering and its tests only; released schema pins remain unchanged. The [review](upstream/2026-10-27-portable-review.json) records the baseline decision. Development HEAD is not a release.

## The alignment request

Nominate a product and technical owner. Identify a native metric your system can responsibly support. Test consented claims from two source systems with two independent agents, then measure consumer decision quality and participation effects. Source-provider issuance, persistent publication, real identity and discovery integration are still future work.

## Distribution

The public repository is Apache-2.0 with third-party notices. `npm run package:review` creates an allowlisted source archive from a clean commit. Executive PDF and Word files are checked in and served by the public site. The validated main branch is deployed to GitHub Pages; local runtime demonstrations still require the Python server. No participant or provider endorsement is claimed.
