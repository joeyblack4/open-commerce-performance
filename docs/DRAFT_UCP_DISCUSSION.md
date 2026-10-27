# LOCAL DRAFT — do not submit

**Title:** Business-first access to scoped merchant outcome evidence

The [business discovery concept](BUSINESS_DISCOVERY_CONCEPT.md) separates candidate discovery, capability discovery and consumer suitability. Our existing experiment is an independently namespaced catalog extension, `ai.black4.commerce.performance`, pointing to opt-in aggregate operational evidence. No merchant score, checkout/payment change or inference of product reliability from shipping/refunds.

Two eligible offers may differ in original-promise versus observed-delivery history, completeness or settled-refund incidence. Useful evidence needs the actual population/window, numerator/denominator, coverage, maturity, policy, source provenance and current consent/status. A signature authenticates origin, not input truth/audit. Missing participation must not become poor performance.

We followed the independently hosted namespace direction in [the October 16 contributor comment on #185](https://github.com/Universal-Commerce-Protocol/ucp/issues/185#issuecomment-6213400329), [Shopify engineering](https://shopify.engineering/UCP) and released `2026-08-25` schemas. The contributor response is not council ratification or endorsement of this project.

## Reviewable example

`examples/ucp/` and `python -m ocp.interop` provide:

1. A business profile and original-shape base catalog/order resources validated against unmodified upstream schemas at `87dd4b1fcff9105d68173120897237fa784c74ef`.
2. A hypothetical **unhosted** HTTPS schema on a namespace-aligned Black 4 origin, `$defs['dev.ucp.shopping.catalog.lookup']`, exact release `requires` and `allOf` composition.
3. A distinct `ocp_evidence` array with merchant-subject aggregate references. No structured objects in the core flat-string `attribution` map or policy/review overload.
4. Narrow exact-version fixture intersection: unsupported client receives unchanged base catalog; opted-in fixture receives references with identical products.
5. Separate local resource and consumer, with explicitly pinned statement/status authority, standard flattened JWS `alg=Ed25519`, scope/method/expiry checks and shopper-specific abstention.

These are not hosted URLs, a full UCP server/negotiator, live fetch conformance or certification. Actual discovery still needs domain authority, TLS, redirect/fetch safety, correct version hosting and client support.

## Reuse and questions

[Open #836](https://github.com/Universal-Commerce-Protocol/ucp/pull/836) proposes transaction correspondence and `unverifiable`; [open #837](https://github.com/Universal-Commerce-Protocol/ucp/pull/837) proposes adjustment causes, including fulfillment mismatch. They may become source inputs if adopted. They are not released fields. Security/risk signals address different transaction concerns.

- How should a consumer discover merchant-scoped evidence before selecting a product: an independent resource, a vendor capability, or a supported business/location reference? The catalog attachment works for offer-first journeys but should not define the whole model.
- How should business, seller, branch and brand bindings be represented without implying scope inheritance?
- Is there a useful existing link relation/identity binding for external issuer claims, or should references stay vendor-defined until multi-party use?
- How could adopted correspondence/adjustment inputs be reused without treating unilateral assertions as audited outcomes?
- Which additional conformance vectors would help evaluate the exact example?

The aggregate excludes consumer/order IDs, suppresses sparse outcomes and diagnostics, and discloses funding/conflicts. Fixed bundles reduce segmentation but do not guarantee privacy. Consent, correction, withdrawal and independent trust remain required; no payment influences verdicts or placement. This asks for technical feedback, not adoption or vendor endorsement. Core promotion would follow EP/DTC governance; the vendor experiment does not masquerade as `dev.ucp.*`.
