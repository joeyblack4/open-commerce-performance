# Portable business evidence for AI recommendations

Open Commerce Performance proposes an open way for businesses to publish evidence about their performance that an agent can consult during discovery and selection. Businesses choose what to publish. A system of record or an identified calculation service attests to a defined result. Any participating AI can check the claim and decide whether it matters to the buyer's request.

The goal is to help consumers choose well and give businesses a way to compete on service they can substantiate. Better recommendations and fairer competition are outcomes to test, not results established by the prototype.

## The proposal

Agree on a common format for publishing business evidence. Leave the choice of metrics open.

A restaurant might publish its average net check or recorded pickup preparation time. An ecommerce brand might publish delivery outcomes when it has the original promise and carrier observations. A B2B service company might publish response time from its support system. Each claim has its own definition, population and limitations. None becomes a universal rating of the business.

A business should be able to authorize publication inside a system it already uses, or through an authorized service using that system. It should not need to operate signing infrastructure or move its records into a new central database. Evidence should be portable across discovery providers and AI platforms.

## How it works

1. **Choose evidence.** The business selects a supported metric and sees its definition, scope and exact publication preview. Reading private records and publishing aggregates are separate permissions.
2. **Calculate and attest.** The source provider or a named service computes the result over the declared eligible population. It discloses missing data and what it actually checked, then signs the claim.
3. **Publish with permission.** The business authorizes the aggregate with its method, source coverage, issuer, measurement period and current status. Private transaction and customer records stay behind the source boundary.
4. **Retrieve and assess.** An agent checks identity, signature, status, method, freshness and relevance. It cites claims that influenced its explanation and identifies unanswered questions.
5. **Refresh and correct.** Later observations produce new versions. Expiry, correction, dispute and withdrawal remain visible; a cached signature cannot restore a withdrawn feed's current status.

The reference is a synthetic demonstration with a public static replay and a local runtime. It is not a global discovery implementation or a source-provider endorsement.

## What the standard defines

| Part | Required meaning |
| --- | --- |
| Business | Responsible entity or location and its identity binding. A branch's record does not automatically describe a brand. |
| Metric | Public, versioned definition, unit, calculation and intended interpretation. |
| Population | Period, service or channel, eligibility, exclusions, sample size and missing-data coverage. |
| Result | Value and supporting aggregate counts, or an explicit unknown or suppressed state. |
| Attestation | Source systems, named issuer, scope of checking, funding relationship and cryptographic protection. |
| Lifecycle | Observation and issue times, expiry, current status and correction or withdrawal references. |

New metric definitions should not require a core protocol release. Providers, businesses and industry groups can define methods. Shared methods enable comparisons; unfamiliar methods need review. Matching names are insufficient: comparison requires compatible definitions, populations, units and windows. An AI must not silently equate different meanings of "on time."

The [claim schema](../spec/schemas/portable-claim.schema.json) and [protocol proposal](PORTABLE_EVIDENCE_PROTOCOL.md) make this concrete. They are a candidate profile, not a ratified standard. The existing 0.2 reference remains a narrower technical example.

## What verification means

**Provider-issued** means the source provider takes responsibility for the declared calculation and scope. **Service-calculated** means a named service takes responsibility for its extraction and calculation using source records. API access does not imply provider endorsement. **Business-asserted** identifies a claim without either source calculation assurance.

A signature authenticates the issuer and protects the signed bytes. It does not establish whether staff entered accurate data or every transaction reached the source. Reproducible arithmetic, complete coverage, independent observation and independent audit are different assurances. The [W3C Verifiable Credentials trust model](https://www.w3.org/TR/vc-data-model-2.0/#trust-model) preserves a similar distinction. This reference uses JWS and does not claim VC conformance.

## Business choice and consumer protection

Businesses choose metrics; they cannot change a published method's meaning or quietly remove unfavorable eligible records. A limited channel or location can be a valid population when prominently disclosed. A verifier accounts for the population it can observe and identifies boundaries it cannot establish.

Voluntary publication remains selective. An unpublished return rate is unknown, not zero. Five favorable measures do not establish superiority over a business publishing one. Shipping performance does not establish product quality; a low refund rate can reflect restrictive policies. New or unconnected businesses retain other routes to consideration.

Publication must minimize private data, suppress unsafe aggregates and consider repeated-release inference. Withdrawal ends current use under the publication contract; it cannot promise deletion of every prior copy. Retention and historical-status rules need agreement before a live pilot. No global customer identity or cross-business purchase tracking is required.

## Where it fits

**Candidate discovery → business identity → relevant evidence → a recommendation for this buyer → existing commerce transaction.**

Candidate discovery comes from search, maps, directories, marketplaces and agent indexes. Evidence helps assess discovered businesses. The agent owns the recommendation; UCP and other supported commerce interfaces carry subsequent catalog, checkout and order interactions. Payment authorization stays with its existing owners.

Evidence should be retrievable without requiring a purchase. UCP's [third-party extension model](https://ucp.dev/specification/overview/#third-party-extensions-comvendor-orgorg) offers an integration option to evaluate. The existing catalog fixture is an offline test against pinned released schemas. No live UCP discovery or platform ingestion is claimed.

Any capable agent could consume this format without an exclusive index or mandatory Black 4 service. Actual use requires AI-platform implementation and choices about trusted issuers. Publication alone cannot make every AI retrieve or trust it. Claim text is data, never executable instructions.

## Participation and competition

For a system of record, permissioned evidence publication could make its operational records more useful to customers outside its own interface. Providers preserve their definitions and source boundaries. Businesses gain portable evidence of improvements in service. AI platforms gain structured support for accountable recommendation explanations.

An open standard needs multiple issuers, affordable participation, transparent methods, public change review and a way to challenge errors. Calculation or hosting fees must not purchase a favorable verdict or undisclosed ranking advantage. Governance should include small businesses and consumers alongside source providers and AI companies. Black 4 is proposing a reference and convening discussion; no consortium or partnership exists.

## The first alignment request

Ask a small founding group of systems of record and AI platforms to:

1. Nominate a product and technical owner to review the format and publication lifecycle.
2. Identify one native metric each source provider could responsibly issue today, including its limitations.
3. Run a consented pilot exchanging claims from two source systems through two independent agent implementations.

First establish that independent consumers interpret portable claims consistently. Then compare the same candidate set with and without evidence. Measure comprehension, realized cost, service outcomes and regret; separately assess smaller-business exposure, participation cost and candidate omissions. Conversion or a changed recommendation alone is insufficient.

The [CEO brief](CEO_BRIEF.md) carries the request. The [walkthrough](SHARE_PACKAGE.md) distinguishes implemented synthetic behavior from the live integrations and adoption still required.
