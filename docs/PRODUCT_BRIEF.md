# Product direction: useful evidence in an agent's commerce decision

**Historical 0.2 build context. The October 27 direction is [portable business evidence](BUSINESS_DISCOVERY_CONCEPT.md), with business-selected metrics and a common claim envelope. The old fixed-bundle requirement applies only to the retained 0.2 fixture.**

Historical build brief; repository publication under Apache-2.0 was authorized on October 26, 2026. See [the licensing decision](LICENSE_RECOMMENDATION.md).

Decision date: 2026-10-25, America/Los_Angeles. Scope: private, local, synthetic prototype.

## Consumer promise

Help a shopper choose among eligible offers using their stated needs and clearly scoped operational evidence. A person should be able to see which facts affected the choice, inspect how a claim was calculated, and understand when the available evidence cannot support a conclusion.

The reference experience starts with three fictional merchants offering a comparable purchase. The shopper can prioritize price or a delivery requirement. The result explains eligibility, tradeoffs, uncertainty, and the evidence used. Merchant operations and product suitability remain separate facts.

## What this build should prove

1. A developer can run the entire example locally from a short quickstart.
2. Shopper priorities change the decision through visible rules. A recommendation can abstain when evidence is inadequate.
3. A consumer implementation can verify signed bytes against explicitly pinned trust configuration and current status. An issuer's verification endpoint alone is insufficient for consumer verification.
4. A third party can inspect the metric definition, cohort, denominator, observation coverage, publication time, historical period, and limitations.
5. Unknown, stale, revoked, disputed, and privacy-suppressed claims retain distinct meanings. Absent participation does not establish poor performance.
6. A compatible agent can use optional evidence while a client without that support retains a valid base commerce flow.
7. The repository supplies reproducible examples, adversarial tests, and a specific ecosystem integration proposal that others can evaluate.

## First experience

Use a clear fictional label throughout. Show a shopper brief, comparable offers, the resulting decision, and an evidence detail panel. Keep technical detail available through drilldown rather than requiring the shopper to interpret raw signatures or JSON.

Offer at least three useful scenarios: price-first, delivery requirement, and insufficient evidence. Explain why an offer qualifies or remains unresolved. The visible output should distinguish facts, deterministic decision rules, and any later model-generated interpretation.

Refund incidence always appears with its policy and scope. It cannot establish product defect rate, satisfaction, or a generally better merchant. Lower incidence under a restrictive policy must not improve a recommendation automatically.

Show the historical measurement period separately from the last data observation and signature expiry. A fresh signature on an old cohort does not establish current merchant performance.

## Interoperability decision

Keep the independent experimental aggregate contract reusable across commerce integrations. Demonstrate a supported UCP vendor integration if the pinned release permits the exact implementation. Preserve original transaction resources and negotiate any extension through the release's actual mechanisms. Unsupported clients must not receive invented fields.

Third-party namespace development does not require promotion into UCP's core namespace. [Shopify's engineering explanation](https://shopify.engineering/UCP) describes independently controlled extensions and capability negotiation. This supports building a concrete vendor experiment before seeking core adoption; actual schema, transport, version, authority, and fetch requirements still govern implementation.

A [UCP contributor response on #185](https://github.com/Universal-Commerce-Protocol/ucp/issues/185#issuecomment-6213400329), checked on 2026-10-25, gives the same practical direction and identifies a composition trap: `allOf` intersects constraints, so an extension must avoid conflicting with a core property's shape. A contributor comment is guidance, not council ratification or endorsement of this project.

If a complete vendor integration cannot be demonstrated within the local build, supply an explicit opt-in companion example with the exact unimplemented integration requirements. Do not suggest a local fixture's hypothetical HTTPS schema URLs are deployed or controlled through the demo server.

ACP integration has a separate contract. [ACP #221](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/issues/221) records unresolved questions about performance fields and documentation differences. It provides a relevant discussion entry point, not permission to add fields to feeds or evidence that ChatGPT ingests this contract.

Google's [official architecture explanation](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/) describes modular capabilities and multiple transports. Use those existing seams where they fit; keep checkout and payments with their existing owners.

## Contribution we can prepare now

Prepare a runnable example and a concise discussion draft presenting the aggregate-evidence gap, the implemented mechanism, a threat model, and questions specific to the protocol's governance. Include the base-client behavior, extension-client behavior, and failing cases.

Track overlap with [UCP #836](https://github.com/Universal-Commerce-Protocol/ucp/pull/836) and [#837](https://github.com/Universal-Commerce-Protocol/ucp/pull/837). Both were open when checked on 2026-10-25. Their proposed transaction correspondence and adjustment-cause semantics could become useful inputs if adopted. Do not duplicate or import unmerged fields as released UCP behavior. Comments on #836 also highlight issuer identity and the limits of third-party recomputation from self-reported inputs.

Demonstrate independently verifiable origin and reproducible calculation separately from source completeness, delivery corroboration, and independent audit. None can be inferred solely from a signature or OAuth connection.

## Priorities within the initial work session

Complete the safe calculator, strict contract, independent verifier, mock adapter, and loopback API. Then make the shopper decision and evidence inspection work end to end. Add the pinned protocol integration example and focused adversarial checks before expanding connectors or presentation breadth.

Use deterministic evaluation cases as regression evidence. Model-based evaluation requires a controlled model/run record; actual consumer benefit requires consented real-world evidence. Report each separately.

Retail Edge supplies the integration reference for existing identity, authority, consent, source execution, and evidence ownership. This project supplies reusable evidence methods and examples. Future integration should use those existing platform owners.

Public release, deployed hosting, real merchant access, outreach, and upstream submission remain separate human decisions. The current build can finish local implementation, local commits, tests, and contribution drafts autonomously.
