# Metric methods 0.2.0

**October 27 update:** the current direction is [portable business evidence](BUSINESS_DISCOVERY_CONCEPT.md). The [0.3 candidate profile](PORTABLE_EVIDENCE_PROTOCOL.md) and local `portable.py` preview add business-selected claims and independent method definitions. The sections below retain the narrower 0.2 implementation and its limits; fixed metrics and bundles are not requirements of the new proposal. Live providers, durable publication and agent-platform adoption remain unimplemented.

The initial handoff is archived in `CODEX_HANDOFF.md`. Runtime definitions live in `src/ocp/metrics.py` and are hashed in each statement. All figures in this repository are fictional.

All cohorts use paid, non-test purchases in a fixed UTC calendar quarter `[start,end)`. Source ledger count may include paid/test exclusions, which remain disclosed through cohort-vs-source reconciliation. No geographic or product slicing API is implemented. Comparison requires identical method, cohort, geography, service, category and refund policy. Missing participation never lowers a score; no score exists.

| Metric | Numerator | Denominator | Follow-up / limitations |
|---|---|---|---|
| `fulfilled_on_time_rate` | Orders delivered by original checkout promise **and** with exact committed SKU quantities delivered | All mature paid non-test purchase-cohort orders, including cancellations/unresolved outcomes | At least 30 days after purchase; immutable checkout-time promise record, separate synthetic carrier outcome, full delivered line quantities. Late/incomplete known outcomes fail; unresolved/missing scans remain unknown. Actual carrier authenticity is not implemented. |
| `order_complete_rate` | Orders whose recorded fulfilled SKU quantities equal original commitment | Paid non-test purchase-cohort orders that reached recorded fulfillment by observation | Conditional fulfillment measure, no doorstep claim. Unfulfilled/cancelled counts remain disclosed; not silently treated as successes. |
| `order_refund_incidence` | Orders with ≥1 settled refund during `[purchase,purchase+60 days)` | Paid non-test purchase-cohort orders with full 60-day observation | Multiple/partial refunds count once per order; cancellation does not remove an order. Refund record creation alone is not settlement proof in a real adapter. Policy friction, denied returns, store credit and chargebacks are not measured. |

For exact observations, `value=numerator/denominator` is an unrounded fraction. The UI rounds to one decimal percent while retaining counts. Zero denominator produces unknown, never 0% or 100%. A fully observed 0-incidence cohort may legitimately have a zero numerator; it still does not imply satisfaction or quality.

`observed` requires source reconciliation, complete metric signals, mature population and privacy release. `partial` publishes **no point estimate**; if the eligible denominator is reconciled, bounds are successes/eligible through (successes+unknown)/eligible. Incomplete entire source rows leave eligible denominator and bounds unknown. Coverage means requisite metric signals observed / known eligible population, not all-channel completeness. `not_observed`, `suppressed` and `disputed` have null point estimates. Conflicting checkout promise versions become disputed. No shipment-to-delivery inference is allowed.

## Privacy release policy

Minimum cohort 30 is a prototype policy, not a privacy guarantee. Suppress the entire statement's numeric fields and source/expected lineage counts for small cohorts, sparse outcome/complement cells, sparse diagnostics (cancellations, unfulfilled, unknown, known, excluded source rows or missing ledger rows), or immature cohorts. Suppressed counts and correlated totals are all null. Tests cover single cancellations/unfulfilled/missing events/exclusions and source-ledger differencing. Fixed quarterly bundles and no free segmentation reduce differencing opportunities; they do not provide differential privacy or protect arbitrary cross-release/complementary disclosures. A real publication program needs a cross-bundle privacy accountant/reviewer using existing governed publication authority.

The schema intentionally accepts only this fixture issuer, three fictional merchant subjects, fixed methods/scopes and explicit synthetic assurance. It is a versioned candidate demonstration contract, not a broad merchant-ready standard. A future portable issuer/subject profile is an explicit versioned design task, not a silent loosening of this validator.

## Deferred metrics

Voluntary repeat purchase is not implemented. It needs a mature 90-day cohort, lawful merchant-local identity linkage, coverage and positive evidence of separately customer-initiated second purchase. Subscription renewals cannot establish it. This mock collects no customer identities.

Product failure/defect, cold-chain safety, spoilage, manufacturer warranty, restaurant seating/noise and consumer satisfaction need separate sources, identities and exposure windows. Ordinary order/refund/fulfillment data cannot establish them. No physical product reliability field or unsupported metric is accepted by the calculator.
