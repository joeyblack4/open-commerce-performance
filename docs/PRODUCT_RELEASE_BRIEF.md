# Next milestone: a product people can understand and an ecosystem can try

**Historical 0.2 build context. The October 27 direction is [portable business evidence](BUSINESS_DISCOVERY_CONCEPT.md), with business-selected metrics and a common claim envelope. The old fixed-bundle requirement applies only to the retained 0.2 fixture.**

Historical build brief. Publication update: on October 26, 2026, the owner authorized public repository distribution under Apache-2.0; see [the licensing decision](LICENSE_RECOMMENDATION.md). Hosted deployment, merchant access and outreach remain separate.

Decision: 2026-10-25. Continue the existing private branch and draft PR. This brief extends the first technical prototype under the user's delegated product authority.

## Outcome

Deliver a polished, runnable reference experience with three coherent paths: shop, participate as a merchant, and build an integration. A visitor should understand the benefit before encountering protocol vocabulary. A developer should be able to reproduce the example and inspect its actual compatibility limits. Actual consumer enthusiasm, merchant benefit, and adoption remain hypotheses for subsequent testing.

## Consumer experience

Lead with a working shopping brief and a result. Keep a concise, persistent fictional-demo label; move detailed clock, standards, and assurance explanations into useful context and evidence inspection.

Replace three hard-coded scenario buttons as the only interface with genuine shopper controls: total budget and a delivery-history preference, with presets as shortcuts. Validate controls and handle impossible combinations. Preserve price-only selection of a merchant with unknown history. Explain the historical threshold in ordinary language and make the rule inspectable. Delivery history cannot promise the arrival of this purchase.

Use distinct, clearly fictional merchant names. Keep the comparison item and availability controlled so operational evidence is the intentional variable. Show the landed price, reason for the choice, meaningful alternatives, and unresolved facts. An eligible low-price option can win for one shopper while a more expensive option fits another.

The main result should answer: which option fits the stated brief, why, what the person pays for that tradeoff, and what the evidence cannot establish. Provide a useful abstention with an actionable adjustment rather than a dead-end warning.

Evidence inspection should show counts, historical period, observation time, coverage, method and source. Translate technical checks carefully: signed origin, internally consistent calculation, publisher recomputation and independently established truth are different facts. Unknowns and sparse samples retain explicit meanings. Do not use refund incidence as a low-is-good ranking signal.

## Merchant experience

Add a merchant path explaining the practical offer: help shoppers and their agents understand the service the merchant actually delivers, using voluntarily shared aggregate evidence. Present recommendation/distribution benefit as a hypothesis, not promised sales lift or platform inclusion.

Include an interactive fictional publication preview. A merchant should see the exact aggregate bundle, its source requirements, what stays private, and what withdrawal/correction means. A demo-only participation/withdrawal simulation must be clearly labelled and must not resemble a real Shopify/Square connection or real publication. Reuse the actual verification and status model wherever feasible. Never let a merchant remove only unfavorable metrics to obtain a better result.

Show concrete source readiness rather than a generic connect button: operational facts available from authorized order/refund records; immutable promises, independent delivery, mature history and product quality that need additional evidence. Absence of access produces unknowns.

Explain merchant incentives and consumer safeguards together: no paid ranking advantage, disclosed verifier relationships, method transparency, publication consent, correction and withdrawal. Avoid certification badges or unsupported independent-audit claims.

## Builder and ecosystem experience

Provide a third path with a short consumer example, machine-readable evidence, the pinned UCP fixture, protocol versions, and an explicit integration diagram. Keep UCP, ACP, AP2 and Square's actual API/MCP surface distinct. Describe a useful boundary rather than presenting every company as an adopter.

Prepare a specific, concise sharing package: a runnable quickstart, screenshots, consumer and merchant walkthrough, architecture/evidence contract, exact compatibility status, contribution question, merchant pilot hypothesis and remaining gaps. Existing research belongs behind this entry point; avoid requiring a maintainer to read a dozen documents before understanding the example.

Refresh official company and upstream sources. Square is a named prospective ecosystem audience; establish what it actually supports before claiming compatibility. A synthetic Square normalization example is valuable only if its field semantics are based on current official docs and its missing evidence remains explicit. Prioritize the consumer/merchant experience and useful integration package over a second shallow connector.

Create a reproducible local release bundle from allowlisted tracked files. Exclude private trust pins, keys, environment files, local paths, ignored artifacts, dependencies and git internals. Include upstream licenses/notices and accurate synthetic-data labels. Prepare an Apache-2.0 licensing recommendation aligned with UCP's reusable ecosystem model; keep the choice and public distribution decision reviewable.

## Quality bar

- Desktop and narrow-screen shopper and merchant paths work, with readable type, accessible names, keyboard operation, clear selection state and no page-level horizontal overflow.
- Loading, empty, error and retry states are visible and tested. Reduced-motion behavior is respected.
- Consumer recommendations use the same tested evidence/policy path as the separate verifier; arbitrary client flags must not turn untrusted evidence into a valid recommendation.
- Shopper inputs and merchant demo actions have meaningful behavioral tests. Existing arithmetic, privacy, isolation, JWS and protocol fixtures keep passing.
- Private PR describes the final product and validation. Demo assets and release bundle reproduce from a clean checkout with documented commands.

## External boundary

The human wants something we can send or publish. Complete the concrete review package first. Continue private repository development and draft PR updates autonomously. Keep public visibility changes, hosted deployment, actual company outreach and upstream submission for explicit authorization of the finished result. Do not access real merchant data or suggest a live platform partnership.
