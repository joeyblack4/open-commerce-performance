# Implementation gap report

Checked 2026-10-25, America/Los_Angeles. Owner: Black 4. Synthetic reference, not merchant certification or a production service.

| Area | Implemented evidence | Practical limit |
|---|---|---|
| Standards | Dated ADR, exact release/HEAD hashes, runnable audit, official link hashes | Bounded open issue/PR searches, no claim all competing proposals found |
| Calculator | Three pure bounded methods, exact populations, maturity, cancellation/line-item handling, coverage, bounds, unknown/suppressed/disputed | Fictional snapshots; Shopify order fields alone cannot establish strict delivery |
| Contract | Draft 2020-12, bounded duplicate-safe parser, semantic arithmetic/population/date/method/privacy validation, negative fixtures | Deliberately fixture-only issuer/subject allowlists; not arbitrary merchant-ready |
| Provenance | Protected flattened JWS via joserfc, fully specified Ed25519, Node crypto interoperability, signed current status | Explicit local TOFU, ephemeral keys/status, no independent merchant identity attestation |
| Consumer | Runnable separate client, pinned keys and status authority; never calls issuer verifier or decision endpoint | Same reference verification code; no access to private-source truth/recomputation |
| Consent/isolation | Withdrawal removes all merchant claims, key revocation/status TTL, supersession/tenant/subject/digest binding tested | No durable consent/audit/correction store or distributed cache/key infrastructure |
| Human path | Shopper-specific choices and abstention, readable inspector, exact counts and unknowns | Publisher recomputation is not independent audit; deterministic policy is not model validation |
| UCP | Offline profile/catalog/order validation and namespaced catalog-reference composition; unchanged unsupported-client products | Unhosted HTTPS fixtures; no live discovery/signature handshake, full negotiation engine or conformance certification |
| Evaluation | Plan saved before deterministic synthetic results, fixed offers/four arms, constraints/abstention | No model runs, blind raters, post-purchase outcomes, power/causal lift or real consumer improvement |

## Acceptance distinctions

A1: official upstream checked; local architecture decided under delegated product authority. No upstream adoption/ratification requested. A2–A5: synthetic labels, aggregate allowlist, strict validation, source-truth/proof separation and adversarial/privacy tests establish reference behavior. They cannot prove a source API captures all economic events or prevent a merchant fabricating coherent input records.

A6: frozen-clock local demo is reproducible. Real-time verification rejects expired statements. No checkout, payments or provider mutation. UCP checks are offline fixture/schema compatibility. A7: no public hosting, deployment, upstream issue/discussion/PR, outreach, customer/provider reads or writes. The human separately authorized the owning private repository; private branch backup/review is distinct from public release.

## Unsupported claims and why

- Real strict on-time/in-full: no immutable checkout promise or independently authenticated complete carrier feed. The mock supplies distinct synthetic signals; fulfilled timestamps cannot stand in for delivery. Fabricated scans remain a source-truth threat.
- Real refund incidence: no settled-refund ledger or mature real source population has been read. Refund creation time alone is not settlement; restrictive policies/denied requests can lower incidence without better outcomes.
- Voluntary repeat: no lawful customer linkage, mature 90-day cohort or proof separating affirmative purchases from renewals. The calculator rejects this metric.
- Product durability, defects, spoilage, cold chain or satisfaction: manufacturer/model/exposure/service evidence absent. Merchant shipping/refunds do not establish SKU reliability.
- Independent audit/corroboration: no auditor or independent source engaged. Fixture recomputation proves arithmetic over that fixture, not source truth/completeness.
- Current merchant quality: the cohort remains Q2 2026 under an October observation and fresh status. This is historical evidence, no current forecast.
- Official UCP/ACP/W3C support: this aggregate/profile is not adopted, hosted or certified. ACP reviews/policy fields are not overloaded. No VC context/cryptosuite profile is implemented.

## Before real pilots

Use Platform Control exact identity/authority/consent and publication Reviews, Connector Hub read transport and MDW governed snapshots. Reconcile complete pagination, counts, coverage and history permission; verify real API/app/protected-data access before a real adapter. Do not inherit unnecessary customer fields because the warehouse already has them.

Persist correction/status/revocation with an existing platform owner, configure real issuer/status trust and protected keys, complete security/privacy review and prove withdrawal/deletion canaries. The [pilot plan](MERCHANT_PILOT_PLAN.md) is not merchant consent or outreach authorization. The [discussion draft](DRAFT_UCP_DISCUSSION.md) is ready for human review, not submission.

Threshold 30 and fixed bundles are conservative prototype controls, not a privacy guarantee or differential privacy. Arbitrary auxiliary data and cross-release differencing remain unproven. Proposed 30-day raw/13-month aggregate retention from the handoff is not adopted or implemented; actual purposes, processing terms and deletion policy need qualified review.

The loopback Python development server is not Internet hosting infrastructure. Keys/consent reset at restart and consumers deliberately re-pin. No deployment manifest exists. Build notices about upstream React `use client` directives are bundler notices. Rendering and remaining verification limits are recorded in VERIFICATION.md.
