# Portable business evidence protocol proposal

Candidate profile 0.3.0 · experimental · October 27 2026

The protocol exchanges optional aggregate claims about a business. It standardizes the evidence envelope and lifecycle while letting metric definitions evolve separately. It defines no ranking formula, universal KPI set, customer identity graph or payment flow.

## Claim and method

A claim binds a business subject, named issuer, public versioned method, population, result, source assurance and validity. The [JSON Schema](../spec/schemas/portable-claim.schema.json) defines the candidate envelope. A method has a stable identifier, version and content digest. Its definition explains the calculation, required records, eligibility, exclusions, unit, privacy and limits. Aggregation names and numeric ranges belong to methods, so a median or signed price difference does not require a core schema change. New methods do not require changing the envelope schema; an agent must understand or explicitly accept a method before interpreting it.

The local demonstration supports six fixed method examples across three fictional businesses. Execution is bounded: no arbitrary queries or untrusted URL fetching. It is not a global method registry. Production adapters, issuer discovery, production method hosting, persistent status and governance remain unimplemented. The public site serves fictional definitions and precomputed claims at a simulated clock; its verification results were recorded during export.

## Issuance and verification

Assurance distinguishes source-provider issuance, service calculation and business assertion. The source and the attesting issuer are separate identities. API access never implies provider endorsement. Signed checks describe the scope of source work; a consumer cannot independently confirm private work by checking a signature.

The reference reuses the Ed25519 flattened JWS mechanism in [ADR 0002](ADRs/0002-jws-profile.md), with a distinct `ocp-portable-claim+jws` type. The 0.2 parser stays unchanged. Strict JSON parsing, schema validation, externally supplied issuer/subject/key bindings, method digest and current signed status are required for the local check. Trust is explicit and local; discovering a key is insufficient.

Publisher reproduction runs on its synthetic snapshot. It is separate from consumer signature and status validation. No raw records or private keys appear in the preview response. Issuer keys are ephemeral and consent/status is not persisted. Source accuracy and independent audit remain unestablished.

## Publication and lifecycle

Businesses may select a subset of supported metrics. Each selected claim retains its declared population and method. There is no user-supplied cohort filter. Unselected metrics contribute neither a success nor a failure.

The read-only preview returns selected claims and signed current status. Withdrawal and dispute previews invalidate use without mutating a shared registry or authorizing publication. Corrected claims should supersede prior versions and preserve identity continuity. Retention, dispute resolution, delegation and revocation transport require agreement and persistence before live use.

## Consumer behavior

Consumers check trusted identity, signed bytes, schema, method binding, period, coverage, validity and status before interpretation. Invalid, withdrawn, disputed or expired claims cannot support assessment. Unknown methods may be transported but are not automatically interpretable. Comparisons require compatible methods and populations. Claim text cannot execute instructions or override consumer policy.

The demo applies a visible deterministic rule for one chosen buyer need. It explains whether an optional claim supports considering the business and lists unresolved dimensions. It is neither a market-wide recommendation nor an LLM evaluation. Refund incidence is never a low-is-good quality signal.

## Recommendation incentives

The [concept](BUSINESS_DISCOVERY_CONCEPT.md#a-responsibility-for-recommendation-platforms) proposes platform participation commitments in addition to claim verification. Assessment against the buyer's request must remain independent of advertising spend, affiliate commission or payment for verification. Sponsored placement and material commercial relationships should be disclosed separately. No commission and missing evidence must not automatically exclude a candidate.

These commitments are outside the signed business-claim envelope. An issuer relationship does not describe every incentive of a recommender. Recommendation disclosure transport, platform enforcement and commercial-incentive tests require pilot design; they are not implemented or certified by this reference. Its bounded interpreter accepts no advertising or commission inputs. The claim schema and existing signature contract remain unchanged.

## Existing standards

Keep evidence independently retrievable. Evaluate references in business profiles, indexes or optional UCP extensions without changing base transaction semantics. The existing offline UCP fixture still targets immutable released v2026-08-25 schemas; the audit records development separately. No live UCP negotiation, ACP ingestion, W3C VC conformance or provider adoption is claimed.

Reuse standard signing. An additional VC profile would require its own conformance work. An open format must not require Black 4 to host every claim or approve every issuer.
