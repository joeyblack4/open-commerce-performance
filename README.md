# Open Commerce Performance

A **local synthetic prototype** for shopper-directed commerce decisions using optional, explicitly scoped operational evidence. No universal score, paid placement, product-quality inference, real merchant access or purchasing.

Three fictional merchants sell the same grocery box at fixed delivered prices. Set a real budget and a 75%, 85% or 95% historical delivery preference; see the choice, its price tradeoff and when there is not enough evidence. Unknown history never establishes poor performance.

Explore **Shop**, **For merchants** and **For builders** in the same app. The merchant path previews the full bundle, withdrawal and dispute through actual status rules without changing the served registry. The builder path leads to the independently pinned consumer, exact protocol fixture and review archive.

For a concise walkthrough and the ecosystem contribution question, start with [the sharing package](docs/SHARE_PACKAGE.md).

## Run in minutes

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/), Node 22.12+ and npm. No API keys, database, OAuth or provider account.

```sh
uv sync --frozen
npm ci --ignore-scripts
npm run build
npm run demo -- --port 8787 --fixture-as-of 2026-10-25T20:00:00Z
```

Open [the shopper demo](http://127.0.0.1:8787). It binds only to loopback. A persistent fictional-demo label identifies the example; About the evidence explains the simulated clock. Fixture data was observed on October 25; cohort dates remain April–June. A fresh signature does not make this old cohort current merchant performance.

**Keep the server running** for the consumer example, in another terminal:

```sh
PYTHONPATH=src uv run python -m ocp.consumer \
  --bootstrap-local --trust artifacts/local-trust.json \
  --fixture-as-of 2026-10-25T20:00:00Z --scenario delivery
```

`--bootstrap-local` is an explicit trust-on-first-use decision for this fictional process, not merchant identity verification. It pins statement keys, exact issuer/subject bindings and a separate signed-status authority. The file contains public keys only. Existing pins are never overwritten. A server restart creates new ephemeral keys: choose a new trust filename and explicitly bootstrap again.

Use custom shopper inputs through the same consumer policy:

```sh
PYTHONPATH=src uv run python -m ocp.consumer --trust artifacts/local-trust.json --fixture-as-of 2026-10-25T20:00:00Z --budget-cents 2500 --priority delivery --threshold 75
```

Repeat using the pins, independently of issuer `/verification` and `/scenarios`:

```sh
PYTHONPATH=src uv run python -m ocp.consumer --trust artifacts/local-trust.json --fixture-as-of 2026-10-25T20:00:00Z --scenario price
PYTHONPATH=src uv run python -m ocp.consumer --trust artifacts/local-trust.json --fixture-as-of 2026-10-25T20:00:00Z --scenario tight
PYTHONPATH=src uv run python -m ocp.consumer --trust artifacts/local-trust.json --fixture-as-of 2026-10-25T20:00:00Z --inject tamper
PYTHONPATH=src uv run python -m ocp.consumer --trust artifacts/local-trust.json --fixture-as-of 2026-10-25T20:00:00Z --inject revoke
PYTHONPATH=src uv run python -m ocp.consumer --trust artifacts/local-trust.json --fixture-as-of 2026-10-25T20:00:00Z --inject stale
```

Expected choices: default delivery → Cedar Market ($24, 900/1000 historical on-time/in-full); price → Little Pantry ($18, unknown delivery); tight delivery budget → abstain. At a 75% threshold and sufficient budget, Grove Goods ($20, 750/1000) is the cheapest qualifying option. A 95% threshold cannot be met; adjustment actions explicitly change the preference and/or budget. All injected failures → delivery abstention. Injection changes only retrieved local objects, sends no mutation, and is not a network attack simulation. The normal verifier uses real UTC when `--fixture-as-of` is absent. Future/expired claims fail; the demo does not disable expiry. `npm run demo -- --real-clock` explicitly uses real time instead.

## Check it

```sh
npm test
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
npm run build
npm audit
PYTHONPATH=src uv run python -m ocp.interop
npm run evaluate
./scripts/protocol_audit
```

The protocol audit uses authenticated `gh` for read-only GitHub access and public official docs. It records timestamped observations; exit 2 means network/source checks incomplete, exit 3 means baseline drift requires review. It never certifies compliance. Tests are offline except loopback HTTP; independent JWS interoperability uses local Node crypto. No tests skip missing dependencies.

## What is implemented

- Versioned JSON Schema 2020-12 and strict parser/semantic validator; positive and adversarial fixtures.
- Bounded pure calculator: delivered on-time/in-full, completeness at recorded fulfillment, 60-day settled refund incidence. Exact counts, cohort/window, coverage, missing states, bounds, maturity and privacy suppression.
- Standard flattened JWS (RFC 7515) through `joserfc`, protected `alg=Ed25519` (RFC 9864), `kid`, `typ`, `cty`; no JWT or W3C VC claim.
- Separate signature/current-status verification, reproducibility and source-truth results. Issuer/subject/tenant isolation, explicit trust, key validity/rotation/revocation and consent withdrawal.
- Read-only synthetic Shopify-shaped adapter; separate synthetic checkout-promise/carrier fields. No real provider client.
- Three-path shopper/merchant/builder app built with free HeroUI and Black 4's approved theme. Budget/history controls, understandable adjustments, source readiness, whole-bundle preview and human evidence inspection keep the technical JSON in drilldown.
- An **offline** UCP vendor-extension fixture validated against unmodified, hash-pinned `v2026-08-25` schemas. Unsupported clients receive unchanged base catalog data; opted-in fixtures receive a distinct evidence-reference field. Hypothetical HTTPS URLs are **unhosted**, not deployed protocol endpoints.

## Local read API

| Resource | Purpose |
|---|---|
| `/v0/.well-known/ocp` | Experimental OCP discovery, explicitly not UCP discovery |
| `/v0/subjects/fictional:merchant-a/performance` | Fixed published bundle, bounded list, no arbitrary segmentation |
| `/v0/statements/{id}` | Aggregate statement; 410 after withdrawal/expiry |
| `/v0/statements/{id}/signature` | Flattened JWS with exact payload bytes |
| `/v0/statements/{id}/status` | Signed current status, payload digest, consent and key revocation; 60-second TTL |
| `/v0/statements/{id}/verification` | Publisher debugging result, not a substitute for consumer verification |
| `/v0/methods/{metric}/0.2.0` | Formula, cohort and limitations |
| `/v0/keys` | Ephemeral public fixture keys; discovery is not trust |
| `/v0/schema/0.2.0` | Experimental schema |
| `/v0/demo`, `/v0/scenarios` | Demo data and preserved deterministic preset traces |
| `/v0/recommendation?budget=2500&priority=delivery&threshold=85&evidence=on` | Bounded shopper preferences; no source cohort slicing or submitted evidence |
| `/v0/merchant-preview?state=shared` | Read-only projection; `shared`, `withdrawn`, `disputed`; served registry is unchanged |
| `/v0/interop` | Offline pinned UCP fixture result |
| `/v0/release-info`, `/v0/release-package` | Prepared private review ZIP status/download; no publication |

All reads use `Cache-Control: no-store`, ETags and security headers. No write API, remote fetches, UCP checkout or ACP feeds. Shopper preference queries never select source cohorts; unknown or duplicate parameters are rejected. GET `/.well-known/ucp` intentionally returns 404. Revocation lives only in this process; restart resets the synthetic demonstration, so this is not a production revocation service.

Read [upstream alignment](docs/ADRs/0001-upstream-alignment.md), [signature profile](docs/ADRs/0002-jws-profile.md), [architecture](docs/ARCHITECTURE.md), [metric rules](docs/METRICS.md), [implementation gaps](docs/IMPLEMENTATION_GAP_REPORT.md), [UCP discussion draft](docs/DRAFT_UCP_DISCUSSION.md) and [consented pilot plan](docs/MERCHANT_PILOT_PLAN.md). No public hosting, outreach, real data or deployment has been authorized by this prototype.

## Prepare a review archive

After committing the reviewed source, run `npm run package:review`. The ZIP in `artifacts/open-commerce-performance-review.zip` contains allowlisted committed source, screenshots, locked dependencies, protocol snapshots, notices and a per-file digest manifest. It excludes dependency directories, environment/key files, git internals, trust pins and machine-local paths. The builder path offers the download only when the archive exists. The archive does not include installed dependencies or a prebuilt dist; the same quickstart works from extracted source. Git is needed to repackage; authenticated gh is needed only for a fresh protocol audit.

[Apache-2.0 is recommended for review](docs/LICENSE_RECOMMENDATION.md), not yet applied to Black 4-authored code. Private development/review is authorized; changing visibility, public licensing/hosting, named outreach, real merchant access and upstream submission remain separate human decisions.

![Shopper controls and tradeoff](docs/screenshots/shopper-desktop.png)
