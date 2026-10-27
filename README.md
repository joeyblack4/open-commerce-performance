# Open Commerce Performance

**Portable evidence about a business that an agent can consult during discovery and selection.**

Businesses choose what to publish. A system of record or named calculation service attests to a defined result. An agent checks the claim and decides whether it matters to the buyer's needs.

The proposal standardizes the evidence format, permission and lifecycle. Metric definitions remain open and separately versioned. The goal is better consumer decisions and competition on service businesses can substantiate.

**Experimental reference · Apache-2.0 · fictional local data.** No provider endorsement, live integrations or AI-platform adoption is claimed.

## Start here

- [CEO brief](docs/CEO_BRIEF.md): the proposal and concrete alignment request.
- [Full concept](docs/BUSINESS_DISCOVERY_CONCEPT.md): operation, commerce-stack fit, incentives and evaluation.
- [Protocol proposal](docs/PORTABLE_EVIDENCE_PROTOCOL.md) and [candidate claim schema](spec/schemas/portable-claim.schema.json).
- [Prepared outreach copy](docs/CEO_OUTREACH.md) and [walkthrough](docs/SHARE_PACKAGE.md).

## Run the concept

Requires Python 3.11+, uv, Node 22.12+ and npm. No API key, database or merchant account.

```sh
uv sync --frozen
npm ci --ignore-scripts
npm run build
npm run demo -- --port 8787 --fixture-as-of 2026-10-25T20:00:00Z
```

Open http://127.0.0.1:8787 in Chrome. The server binds only to loopback.

1. Choose a restaurant, ecommerce brand or B2B service company.
2. Choose either of its two example metrics, both or neither. Inspect the aggregate, population, source, issuer and signed claim.
3. Change the buyer's need. The explanation cites applicable evidence or says the requirement is unknown.
4. Preview withdrawal or dispute. The signed claim can no longer support the assessment.

The six example methods are not a required KPI list. All use the same 0.3 candidate envelope. A new public method can use the envelope without changing the core schema; the consumer still has to understand it. The local runtime recognizes only the bounded fictional methods and fetches no remote definitions.

The demo calculates, signs and checks generated records. Source accuracy and independent audit are unestablished. Its visible deterministic interpretation is not an LLM or global market recommendation. Publication selection and status are read-only previews, not real merchant authorization or persistent publication.

## What a claim carries

| Part | Purpose |
| --- | --- |
| Business and issuer | Who the evidence describes and who stands behind the calculation |
| Method and version | What the number means, its unit and how it was calculated |
| Population and coverage | Which records and period it covers, exclusions and missing observations |
| Result | The value or an explicit unknown state |
| Assurance | Source-provider issuance, service calculation or business assertion, kept distinct |
| Validity and status | Observation time, expiry, withdrawal, dispute and correction |

Merchants choose metrics, not handpicked favorable records inside a declared population. Missing publication is unknown. Signatures establish origin and integrity, not source truth. Neither metric count nor refund incidence creates a universal quality score.

## Local resources

| Resource | Purpose |
| --- | --- |
| `/v0/portable-preview?business=restaurant&claims=pickup&state=published&need=pickup` | Bounded read-only publication and interpretation preview |
| `/v0/portable-schema`, `/v0/portable-methods` | Candidate 0.3 envelope and local method definitions |
| `/brief.md`, `/concept.md`, `/protocol.md` | Executive and technical proposal |
| `/brief.pdf` | Executive PDF when separately prepared locally; Markdown remains available |

No generic file serving, arbitrary cohort queries or provider writes are implemented. Existing 0.2 signed-evidence, status, consumer and comparison routes remain for technical regression and interoperability work. The UI's **Comparison reference** and **For builders** paths expose that earlier narrow experiment. Its three-measure fixed bundle does not define the new optional-publication proposal.

## Verify

```sh
npm test
npm run build
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
PYTHONPATH=src uv run python -m ocp.interop
npm run evaluate
./scripts/protocol_audit
```

The protocol audit reads official sources using authenticated gh. Exit 2 means incomplete checks; exit 3 means upstream drift needs review. It never certifies compliance. The offline UCP fixture uses unchanged pinned released v2026-08-25 schemas, not live negotiation. The reference uses flattened JWS, not a W3C VC profile.

## Align on the standard

The initial ask is to nominate product and technical owners, identify a native measure each source system could responsibly issue, and test exchange between two source systems and two independent agents. Consent, completeness, identity, comparison and correction are part of the test. Consumer benefit must then be measured.

The protocol should be openly usable across source providers, issuers and AI platforms. A Black 4-hosted service should be optional. No consortium, provider partnership or recommendation inclusion has been agreed.

[Architecture](docs/ARCHITECTURE.md) · [0.2 methods](docs/METRICS.md) · [signature profile](docs/ADRs/0002-jws-profile.md) · [0.3 direction](docs/ADRs/0003-portable-business-evidence.md) · [validation](VERIFICATION.md) · [implementation gaps](docs/IMPLEMENTATION_GAP_REPORT.md).

## Share the reference

The repository is public under Apache-2.0. LICENSE, NOTICE and third-party notices apply. `npm run package:review` builds an allowlisted archive from clean committed source, excluding credentials, trust pins, dependencies and local artifacts. The executive PDF is a separately prepared local deliverable; it is not required to run the source archive.

Public hosting, real merchant access, company outreach and upstream submission require their applicable authorization. None is performed by the demo.
