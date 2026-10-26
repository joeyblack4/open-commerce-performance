> Archived handoff context. Current implementation: ADR 0001/0002, METRICS.md and IMPLEMENTATION_GAP_REPORT.md supersede historical decisions and pending items below.

# Threat model, privacy, verification and incentives

## Threat actors / failure modes

| Failure mode | Consequence | Mitigation / evidence |
|---|---|---|
| Seller selects only flattering metrics or subsidiaries | Metric shopping masquerades as neutral outcomes | Registry of published/withheld metric categories; merchant identity and covered channels/locations; do not penalize nonparticipants; standardized mandatory bundle if public certification sought |
| Seller omits failed/cancelled orders or changes promise | Inflated delivery rates | Immutable source-event inclusion ledger; predefined denominator; correction/reconciliation; committed checkout promise from independent snapshot; cancellation cohort |
| Low refunds because returns are difficult | 'Good quality' inference inverted | Show return policy and declined requests with refund incidence; triangulate with independent complaint outcomes |
| Affiliate/pay-for-promotion verifier | Commercial interests affect assertions | Public compensation/conflict statement; issuer-level audit; prohibit payment-linked positive verdicts; governance independent of commercial sales |
| Merchant-authenticated source still incomplete | Misleading verified label | Separate authenticity vs completeness vs calculation vs independent corroboration; declare observation coverage and limitations |
| Hacked connector or breached tokens | Customer/order data exposed | OAuth least privilege, encrypted tokens, segregated per-tenant storage, rotation, kill switch, deletion and access audit logs |
| Merchant/customer PII leakage through aggregates | Reidentification, profiling | Threshold k >= 30 for all published cohorts initially (pilot policy not a universal privacy guarantee); suppress sparse geo/SKU segments and differences between overlapping aggregates; rate limit; no public customer IDs/hash; privacy review |
| Repeated metric differences reveal single transactions | Differencing attack | Fixed reporting periods, coarse segments, minimum cell size and cohort-overlap suppression; audit privacy risk |
| Signature spoof, stale keys, tampering | False proofs | Proper signature verification, trusted issuer registry, public key rotation, revocation, expiry, replay protections and canonical bytes |
| Agent interprets unsupported metric as 0 | Wrong ranking | Explicit status enum, `value:null`, deterministic negative tests; explain unknowns |
| Discriminatory proxy, geography, firm size | Smaller merchants penalized despite performance | Stratify on comparable service/geography; report uncertainty; fairness evaluation; no requirement to pay or publish |
| Data extraction from public merchant profiles | Competitive intelligence / privacy harms | Publish only merchant-authorized aggregates, carefully segmented; cap exposure and full statement history |
| Manipulative merchants bundle or split orders | Games denominators | Reconciliation to settled charge/order grouping and anti-fraud duplicate normalization |
| Cross-platform duplicates | Inflated volume/repeat cohorts | Canonical source event IDs kept privately; source-tagged transaction lineage; dedupe across connected channels if consented and technically supportable |

## Verification semantics (avoid 'verified' inflation)

1. **Cryptographically authentic:** bytes were signed by key associated with named issuer; key and status verified. Proves neither honesty nor accuracy.
2. **Platform-linked:** source API connection exists; authenticity of the API and snapshot lineage checked. Doesn't prove completeness of other fulfillment channels.
3. **Methodologically reproducible:** calculator version and input coverage manifest are documented; recomputation over same data matches result. Doesn't establish completeness of source records.
4. **Independently corroborated:** separate independent carrier/helpdesk/processor data support relevant event classes and sampled claims.
5. **Audited:** a truly independent qualified auditor performs scoped controls/test procedures; audit scope, dates and exceptions public.

Claims can express each dimension independently; avoid a universally flattering overall `verified` badge.

## Privacy/security checklist

- Contract and API must be aggregate only; never include names, addresses, email, phone, payment tokens, raw transaction/order identifiers or cross-site unique customer hashes.
- No customer PII retained unless strictly required and merchant/customer processing terms permit it; prefer aggregation at connector boundary with nonreversible, merchant-local ephemeral linkage.
- Data processor agreements, lawful basis for processing and cross-border transfer review before production; verify CCPA/CPRA and applicable laws with counsel.
- OAuth/token permissions read-only. Never store tokens in signed documents, logs, developer fixtures or crash reports.
- Allow merchant withdrawal; do not erase historical tamper-proof attestations in a misleading way: mark revoked and honor applicable deletion obligations while balancing immutable accountability.
- Data minimization and retention: proposed 30-day raw ingestion window and 13-month aggregates pending legal/security review; document actual policies. Delete on disconnect, except legally required records.
- Human review of unexpected scope elevation, stale/revoked evidence, suspicious changes, and collisions; risk register and incident playbook before real merchants.

## Incentive design

Public basic schema and verifiers should be freely accessible. Any paid verification/analytics must not influence calculation results or preferentially rank merchants. Independence of the operator is a governance question: publish who funds issuer, verifier, agent integration, and any affiliate relationship; audit conflicted decisions. Program must permit negative, qualified, and corrective claims, with right to dispute methodology without secretly removing unfavorable source evidence.
