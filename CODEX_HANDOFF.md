# CODEX: EXECUTION HANDOFF — 2026-10-25

## Paste this exact mission into a new Codex project/thread

You are Codex engineering lead for Black 4's *Open Commerce Performance* initiative. Read the files in this package before editing. Execute the work, not just create a plan. The purpose is better consumer decisions using voluntarily published, independently verifiable commerce-operation evidence, without preferential treatment for merchants that pay for promotion.

**ABSOLUTE PRIORITY #1: compatibility with the most current official UCP, ACP, AP2 and adjacent standards.** Begin by independently reading the upstream specifications, release notes, open issues/PRs, governance process, and SDK/conformance tests as of execution date. Write a dated `docs/ADRs/0001-upstream-alignment.md` with links and commit/tag hashes. Treat `v2026-08-25` as the last verified UCP published release as of handoff, NOT as a permanent latest version; verify again before proceeding. Document what UCP solves, what it doesn't, whether trust/performance should be an independent capability, third-party extension, external referenced credential or another supported mechanism. Never inject unsupported fields into UCP schemas and call them UCP-compliant. Prefer an interoperable external signed evidence resource while upstream governance is unresolved. Reuse UCP discovery, version negotiation, canonical schema rules and namespace authority verification ONLY when valid according to official specs.

**ABSOLUTE PRIORITY #2: honest claims.** A merchant OAuth connection is not a data audit. A cryptographic signature is not a true-data guarantee. Preserve what was directly observed, what was self-reported, what was derived, what was corroborated and what remains unknown. Never conflate merchant quality with a particular SKU's physical reliability.

**ABSOLUTE PRIORITY #3: avoid harm.** No consumer-level data published, no raw order/customer identifiers in public payloads, no dark-pattern consent, no purchasing or writing to source-commerce systems, no financial incentives affecting certification verdicts. Tenant-isolated data, least-privilege access, revocation, transparency, anti-gaming safeguards.

### Context / placement

Investigate `joeyblack4/black4-retail-edge` and Black 4's existing Platform Control, Connector Hub, integrations, evidence tooling, review ledger and Codex gates before choosing deployment. Treat customer infrastructure as protected. If the repository is not accessible, keep this standalone and generate a clean integration RFC—DO NOT recreate platform services or presume permission. Preserve the current repository's AGENTS.md, CI, branch protection and deployment policy. Local repo is source of truth; use feature branch + PR, review/tests and human canary before any deployment. No production authorization is implied.

### Work order

**P0 — protocol reconnaissance (must finish before major implementation)**
1. Read upstream UCP docs, latest released tag + HEAD, GitHub governance/EP guidance, open trust/reputation/merchant quality proposals, samples and conformance. Read OpenAI ACP product feed and checkout docs, Google AP2, A2A/MCP transport applicability and W3C VC Data Model 2.0. Gather exact deep links and versions.
2. Create compatibility matrix: what each standard addresses, where OCP could connect, known constraints, version risks, and missing capabilities; identify direct overlap and avoid it. Record any existing competing proposal. Compare three integration mechanisms: (a) UCP third-party namespaced capability, (b) independent evidence endpoint referenced from a standards-compliant profile, and (c) external registry that an agent may opt into. Do NOT decide (a) simply because it sounds native.
3. Write ADR-0001 with explicit decision, alternatives, upstream feedback needed and zero unsupported conformance claims. Update working spec if upstream differs from this handoff.

**P1 — rigorous data and evidence model**
4. Define metrics with canonical numerator/denominator, measured time windows, units, exclusions, segmentation, sample-size privacy suppression, missing-data semantics, comparator policy, precision and manipulation risks. Treat latency of data and return-lag censoring explicitly. Start with `fulfilled_on_time_rate`, `order_complete_rate`, `order_refund_incidence` and no more than one carefully qualified repeat-purchase cohort measure. The first two require promise/delivery and line-item data; mark unsupported instead of approximating silently.
5. Implement versioned schema, parser/validator, sample fixtures, bounded metric calculator over synthetic event data, signed-statements verifier with key rotation/revocation design, and metadata-rich public endpoint. Keep calculation proofs separate from cryptographic provenance. Use external W3C VC profile only after checking its mandatory security requirements and interoperable cryptosuite; don't invent VC-looking JSON.
6. Build a read-only mock Shopify adapter first. Implement a real Shopify connector only with merchant consent, approved access, app reviews and minimized scopes; Square adapter second. If access to `read_all_orders` or customer identities is unavailable, publish `not_observed` and coverage, not a fictional 90-day voluntary repeat rate. Do not assume fulfillment event timestamp equals delivered-to-consumer timestamp.
7. Expose agent-readable evidence + verification result + source lineage, human-legible performance page, signed JSON if feasible, and a simple demonstration tool (MCP only if useful and implemented correctly). No public advertising rankings or global one-number score.

**P2 — validation of better commerce**
8. Build preregistered blinded recommendation evaluation: same agent/model and candidate choices with and without valid operational evidence, control for price/attributes/availability, measure recommendation regret and constraint satisfaction on synthetic cases; then opt-in real pilots and actual post-purchase feedback where lawful. Add adversarial cases: merchant with strict no-refund policy, coerced subscription renewal, segment cherry-picking, selective publication, low sample sizes, fabricated delivery scans, skewed geography and review manipulation.
9. Pilot with 3–5 consenting, distinct Shopify merchants. Before outreach, define baseline, legitimate data-access basis, consumer benefit hypothesis, publication authorization, data removal, dispute and correction processes. Do NOT advertise independently audited metrics without an actual audit.

**P3 — standards adoption**
10. Create a concise public GitHub discussion for UCP maintainers presenting gap, use cases, threat model and concrete proposed mechanism, explicitly asking whether they prefer independent evidence + linking versus third-party capability. Only after feedback and proof should an enhancement proposal be submitted. Draft ACP-facing enrichment proposal separately; do not suggest ACP/UCP are the same protocol.

### Mandatory first deliverables

- `docs/ADRs/0001-upstream-alignment.md` (current-state matrix with dated upstream links, release/tag and SHA)
- runnable `scripts/protocol_audit` that checks official upstream tags/links and produces date-stamped snapshot; warn on network failures
- `spec/schemas/...` + schema tests + negative tests + fictional sample claims
- `src/` core aggregate metric calculator and provenance verifier with unit tests
- `src/adapters/shopify_mock` + local demo endpoint using fictional synthetic order events
- `docs/IMPLEMENTATION_GAP_REPORT.md` with blocked/unverified claims, privacy constraints and why unsupported KPIs are unsupported
- draft UCP community discussion and merchant pilot plan

### Hard gates for review

- A1: upstream protocol version checked and compatibility ADR approved.
- A2: no assertion of standard adoption, independent audit, carrier proof or product-defect rate without grounds.
- A3: all public numeric claims have population, denominator, window, coverage, evidence type, verifier and signature status.
- A4: no PII in public contract, robust multi-tenant isolation, consent revocation and key revocation.
- A5: deterministic adversarial tests pass; missing/conflicting evidence is exposed, never coerced to zero incidents.
- A6: reproducible local demo and protocol tests pass; no checkout/payment scope creep.
- A7: no production/customer data changes or public standards submission without explicit human review.

### Report format at the end of Codex work

Summary / code files / upstream citations with exact versions / commands + tests run / demonstrated outputs / failing & blocked checks / security concerns / open governance questions / PR URLs / what requires human approval.
