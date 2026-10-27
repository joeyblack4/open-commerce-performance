# Architecture and future integration boundary

Owner: Black 4. Status: local synthetic reference, 2026-10-25.

`mock snapshot → pure calculator → aggregate allowlist projection → strict validator → JWS → local GET → independently pinned consumer → shopper policy`

The human interface is a static React/HeroUI build served by the same loopback-only demonstration process. It creates no database, production service, scheduler, credential store, customer registry or general workflow engine. All raw fixture orders stay private to the process. Public contracts contain aggregate counts and fixed methodology, not order/customer identifiers or input-row hashes.

## Placement

The owning repository is `joeyblack4/open-commerce-performance`, created privately at the human's request and authorized for public Apache-2.0 distribution on October 26, 2026. Retail Edge was inspected at commit `0b7a1ac25f31dbdeffe6c810c758f39a1c86d9e3` and remains a read-only reference. No Retail Edge code changes are required by this prototype. Its original untracked output was preserved; the unused managed worktree was archived without OCP changes.

Inspected ownership and actual code:

| Existing owner | Integration boundary |
|---|---|
| Retail Edge `apps/platform-control/api/src/operations` and `packages/contracts/src/operations` | Canonical operation definitions and implementation; a graduated user capability must ship through the existing MCP registry and human UI in the same change. No manually registered tool here. |
| Platform Control business authority, capability bindings, Reviews and context layer | Exact business/actor/subject mapping, connection permissions, consent to processing versus publication, revocation/correction authority and immutable review/receipt. The in-memory demo flags are fixtures, not a competing authority model. |
| Connector Hub/Nango | Merchant-authorized read transport and credentials. Future adapter calls exact business connections. No OAuth/token storage here. |
| MDW `mdw/platform/warehouse/ingest/providers/shopify.py` | Existing Admin GraphQL source (pinned `2026-07` in the inspected code), tenant capture and coverage. Raw order/marketing capture includes order/refund evidence but does not establish immutable checkout promises or independent final delivery scans. No changes made to its ingestion scope. |
| MDW tenant warehouse and `warehouse/sample_evidence.py` | Source ownership, provenance/freshness, immutable input snapshots and count reconciliation. Reuse those before exposing a pilot. |

A real integration should supply the calculator a minimized, authorized, source-reconciled snapshot from MDW. It must validate original promise versions, independently sourced delivery events and all line-item pages, then freeze the precise method and cohort. Platform Control must bind publication consent to the exact bundle/revision and serve current correction/revocation through its existing authority. Nothing in this repository grants itself access to that data.

## Evidence and lifecycle

Statements are immutable signed byte resources. The separate current-status response references the exact SHA256 of those bytes and a superseding statement where applicable. The private process maps tenant+subject to each statement; consumers pin that binding. Consent withdrawal removes every statement for that merchant while leaving minimal tombstone/status data; old cached signatures cannot restore authority. Keys and statuses expire; outage fails closed. Future correction requires a new statement ID, an explicit supersession relation and existing reviewed publication authority. The prototype tests supersession status but has no durable correction editor or audit log.

All synthetic keys are independently generated per tenant in memory and disappear on restart. A separate in-memory signing key is the status authority. Consumers explicitly pin its public key; an endpoint saying 'valid' does not establish trust. Status TTL is 60 seconds. The local server emits no-store, ETag, CSP, no-referrer and nosniff, restricts Host/Origin, bounds/rate-limits reads, rejects arbitrary cohort query parameters and serves no write endpoint. This is developer isolation, not an Internet hosting design.

## UI foundation

Free HeroUI React/styles `3.2.6`, Inter, Black 4 black accent/neutral base, Medium radius and Large form radius. `web/black4-theme.css` is an unchanged copy of the approved Black 4 shared export from Retail Edge at the revision above, retained as an explicit cross-repository snapshot. No monorepo dependency or alternate theme is introduced. Controls/dialog geometry and focus behavior remain native; CSS owns layout. This repository does not migrate or deploy any existing product application.

Visual thesis: quiet neutral workspace, readable numbers and visible uncertainty. Content plan: shopper priorities, decision with reasons, comparable evidence, proof drilldown. Interaction thesis: native selection feedback and modal/disclosure transitions, with reduced-motion behavior inherited from HeroUI; no decorative motion or marketing imagery in this utility interface.

## Three-path product experience

The same static app offers Shop, For merchants and For builders. Shopper preferences are bounded GET parameters (budget 1500–3000 cents, price/delivery priority, 75/85/95 historical threshold and evidence on/off). They never alter source cohorts. Recommendations and feasible adjustment actions are calculated server-side from the registry's verified evidence, through the same pure policy used by the independently pinned consumer; callers cannot submit verified flags or evidence.

Merchant preview uses a copied in-memory consent/status projection for shared, withdrawn and disputed states. The original registry, keys, snapshots and publication state remain untouched. It shows the complete metric bundle or its status consequence, never a favorable-metric selector. Real connection/publication/consent authoring is absent.

The builder path exposes pinned protocol fixtures, consumer commands and a prepared review-archive download. The deterministic allowlist exporter reads only clean committed HEAD blobs, retains notices and per-file digests, and excludes credentials, pins, dependencies, git state and local paths. It does not publish, grant a license, create a hosted service or contact an ecosystem participant.

## Business-first concept revision — October 26, 2026

The [concept paper](BUSINESS_DISCOVERY_CONCEPT.md) describes candidate discovery → exact business identity → current eligibility/relevant evidence → consumer-specific choice → existing commerce rails → consented outcome measurement. These are responsibilities, not new deploy units. The current app adds an interactive explanation and a closed-world business-fit experiment. `/v0/business-discovery` accepts the existing bounded preferences plus one of three fixed need contexts. Only the shipped-order fixture is in scope; pickup/meal contexts retain seeded identities but return no decision, including for price-first requests. Market coverage stays unknown. No new directories, external reads, cohort slicing, brand identity, auth or UCP endpoints were added. `/concept.md` serves only the checked-in concept paper.
