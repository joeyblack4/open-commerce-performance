# Product verification — 2026-10-26

## Consumer discovery framing October 27 2026

The live-page narrative and executive proposal now lead with advertising, affiliate and sponsorship incentives and the costs a consumer can bear after a poor choice. The concept cites Google's auction explanation, FTC guidance and a dated enforcement case, and a 2018 affiliate-disclosure study. Historical findings are not presented as current market prevalence or proof that all recommendations are compromised.

The proposal adds explicit AI-platform responsibilities and a pilot test holding evidence and buyer intent fixed while varying commercial incentives. These are proposed commitments. No incentive-disclosure transport, ranking enforcement, new claim field or live platform integration was implemented. Existing optional claims, provenance boundaries and deterministic interpretation remain intact.

All 87 Python and 18 React tests pass. Hosted TypeScript/Vite build, Ruff, format and diff checks pass. The fresh official-source audit completed with `reviewed_snapshot_unchanged`. Both pages of the revised executive PDF were rendered and visually inspected. Connected Chrome checks confirm the revised page and mobile evidence overlay at 390px without horizontal overflow; temporary viewport overrides were reset. The versioned release records public deployment verification.

## Public distribution October 27 2026

Public synthetic hosting and proposal publication were authorized October 27. GitHub Pages serves a static bundle with all 72 fictional preview combinations and a normal HTTPS proposal PDF. `publication.json` binds exported bytes to the deployment source commit. No Python server or live provider access is exposed.

87 Python and 18 React tests pass, including static export coverage, omission and withdrawal behavior, public-key-only export, PDF presence, manifest digests and strict hosted file lookup. The hosted Vite build, Ruff, formatting and relative documentation links pass. The two-page PDF was regenerated with its main-branch reference and both rendered pages inspected. The exact static build was exercised in connected Chrome under its deployment subpath before publication.

The Pages workflow validates pull requests and deploys main after checks. Live publication and download verification are reported in the GitHub release; the demo's origin/status results remain recorded synthetic checks at the declared fixture clock.

## Portable business evidence rewrite October 27 2026

The current concept uses business-selected claims in a generic 0.3 candidate envelope. Six separately versioned methods across restaurant, ecommerce and B2B examples use the same schema. The original 0.2 calculator, verifier and offline UCP fixture remain unchanged technical references.

- 84 Python tests and 16 React tests pass. New checks cover optional publication, omission as unknown, cross-subject and cross-method isolation, method digest and population binding, missing observations, expired or withdrawn status, signature tampering and fixture authority limits. UI checks cover changed buyer needs, empty publication, failure/retry, citation inspection and focus restoration.
- TypeScript/Vite build, Ruff, formatting and diff checks pass; npm audit reports no vulnerabilities. Existing deterministic evaluation and pinned offline UCP fixture pass. No real AI, source provider or consumer outcome was evaluated.
- Connected work-profile Chrome verified all three business examples, metric omission, withdrawal and citation inspection. Desktop and 390px layouts have no horizontal overflow; mobile overlays remain readable and dismiss correctly. Temporary viewport overrides were reset.
- The two-page executive brief was rendered and visually inspected. Its reference links to the current proposal branch. Prepared email copy has not been sent.
- Official-source network checks completed. UCP development HEAD changed only documentation rendering and its tests relative to the prior baseline; the review records that decision. Released schema pins are unchanged. No conformance or adoption claim follows from this review.

Current screenshots: [desktop](docs/screenshots/portable-desktop.png) and [mobile](docs/screenshots/portable-mobile.png).

Repository `joeyblack4/open-commerce-performance`, implemented in PR #1. The owner authorized public distribution under Apache-2.0 on October 26, 2026. Source and synthetic demo only; no live merchant data, production deployment, named outreach or upstream submission.

## Automated checks

| Check | Result |
|---|---|
| Clean `npm ci --ignore-scripts` using the locked dependencies | Passed; standard npm installation works |
| `npm test` | **75 Python tests + 11 React UI tests passed**, no skips |
| `uv run ruff check src tests scripts` and format check | Passed |
| `npm run build` | TypeScript/Vite passed; upstream HeroUI `use client` bundler notices remain informational |
| `npm audit` | **0 vulnerabilities** |
| `python -m ocp.interop` | Offline immutable UCP schema validation and narrow fixture intersection passed; unsupported-client products unchanged |
| `npm run evaluate` | 12 deterministic preset/arm cases; no selected offer violates hard price/availability constraints |
| Product preference matrix | All **192** budget/priority/history/evidence combinations match independently specified fixture choices |
| Adjustment actions | Each proposed combined budget/threshold or price-only adjustment produces an option meeting the preferences it explicitly states |
| Review exporter | Fixed timestamp/order and per-file digests; repeated exports byte-identical; tracked environment material excluded; dirty source refused |
| Markdown relative links and `git diff --check` | Passed |
| Fresh protocol audit | Network complete, reviewed UCP/ACP/AP2 baseline unchanged; adjacent Poppy metadata and official ecosystem links recorded |

The extensionless protocol-audit script is explicitly included in Ruff checks. Locked test dependencies were updated to Vitest 4.1.12 and happy-dom 21.0.4 after their earlier versions produced audit findings. A one-time npm 11 resolver invocation handled an npm 10 peer-resolution crash during dependency updates; the resulting lock was then installed successfully with the normal `npm ci` command. No global npm installation or user configuration was changed.

Exact primary-source observations are in `docs/upstream/2026-10-25-ecosystem-refresh.json`. Poppy deployed docs redirect to working Draft 0.3 while public repository metadata lists 0.2/0.1; no released 0.3 or OCP/Poppy conformance is inferred. No Platform Control or MDW code changed, so unrelated monorepo/deployment suites were not run.

## Consumer, shopper and merchant paths

The implementation server uses `http://127.0.0.1:8787`; independent review used a fresh isolated server at `http://127.0.0.1:8788`. Both use explicitly simulated fixture clock `2026-10-25T20:00:00Z`. Normal consumer verification uses strict real UTC unless that fixture clock is explicitly supplied.

| Condition | Demonstrated result |
|---|---|
| $25 budget, 85% historical delivery preference | Cedar Market, $24, 900/1000 historical on-time/in-full; explains the $6 tradeoff against the lowest price |
| $20 budget, 75% preference | Grove Goods, $20, 750/1000; explains the $2 tradeoff |
| Price first | Little Pantry, $18; delivery history remains unknown |
| $19 delivery-first or a 95% requirement | Abstention; adjustment choices explicitly alter the relevant budget and/or history preference |
| $15 budget | No affordable offer; a price-only action raises to the feasible $18 option rather than promising a nonexistent one |
| Payload tamper, withdrawn consent or stale status injection | No current evidence; delivery abstention |
| Consumer clock 2027-01-01 | Expired fixture rejected; delivery abstention |
| Merchant shared / withdrawn / disputed previews | Actual status verifier used; full three-measure bundle or no usable public claims; live registry retains all nine statements |

The separately pinned consumer verifies all nine actual JWS envelopes without calling issuer `/verification` or `/scenarios`. It accepts custom budget/priority/threshold inputs and uses the same policy as the UI API. Signatures, semantic arithmetic, current permission and private-source reproduction remain distinct. Python/joserfc ↔ Node crypto interoperability tests pass. A valid signature on coherent fabricated figures still does not establish source truth.

## Point-in-time browser QA

- Connected Chrome desktop: shopper controls, result/tradeoff/unknowns, evidence drilldown, full merchant bundle, withdrawal/restoration and builder entry point. Screenshots are tracked under `docs/screenshots/`.
- Independent clean testing session at **390×844**, with reduced-motion emulation: no page-level horizontal overflow; mobile “See my options” moves the result to approximately 16px from the viewport top.
- Keyboard: budget Home reaches $15; five ArrowRight steps reach $20; changing to 75% selects Grove; 95% abstains; the combined 85%/$24 adjustment selects Cedar.
- Evidence dialog Escape closes it and focus returns to the originating evidence button after focus-scope settling. No active animation remained after closing in reduced-motion mode.
- All three paths fit a **320px** viewport (document width approximately 305px including scrollbar).
- Real browser request aborts for initial `/v0/demo` and subsequent `/v0/recommendation`: understandable error, no stale recommendation, and retry recovers after network restoration.
- React tests additionally cover loading, missing published evidence, initial error/retry, stale-result removal, merchant preview states, developer entry and human-first evidence disclosure.

These are focused observations, not full accessibility certification, a comprehensive device matrix, blind consumer comprehension research or proof people will love the product. Real merchant benefit, source authenticity/corroboration, independent audit and actual platform adoption remain unproven.

## Review package

`npm run package:review` exports only allowlisted committed source and screenshots, with the upstream license/notices and per-file SHA256 manifest. It refuses machine-local paths and known private-key material, excludes environment/key files, pins, dependencies and git internals, and requires clean committed source. The archive is an experimental reference snapshot including the Apache-2.0 LICENSE, NOTICE and retained third-party attribution.

The final archive is rebuilt after each source commit. Its exact commit, bytes and digest are reported by the exporter and final handoff, avoiding a self-referential hash in this source document. Clean extracted-source reproduction and archive inspection are performed before handoff; any remaining failure is reported explicitly rather than called a public release.

## Publication preparation — October 26, 2026

Applied the owner-approved Apache-2.0 license and NOTICE, retained unmodified upstream attribution, updated package metadata and public archive labels, and required both root license files in the exporter. Re-ran all 69 Python and 9 React tests, TypeScript/Vite build, Python lint/format and diff checks successfully. The locked Python environment remains valid. Relative documentation links resolve.

Reviewed all 175 pre-publication historical file blobs for known credential-token/private-key patterns, machine-local paths and unexpected tracked environment/dependency/artifact paths; no matches were found. This is a bounded content check, not a guarantee against every possible secret format. Prior screenshot review found fictional content only.

The fresh official-source audit detected UCP development HEAD changes and was reviewed explicitly, as documented in ADR 0001 and the dated publication snapshot. Released schemas are unchanged. Evaluating that snapshot against the updated reviewed baseline passes; the original drift result is retained in the snapshot for provenance.

Public repository distribution is authorized. The demo remains local and synthetic; no hosted deployment, real merchant access, company outreach or upstream submission accompanies publication.

## Business discovery concept — October 26, 2026

The app adds The concept and renames Shop to Compare, identifying the merchant as the comparison subject and the identical basket as controlled context. The deep concept paper is available through the fixed `/concept.md` read route and the app download. No generic filesystem route was added.

Six new Python tests cover different consumer winners, unsupported pickup/meal scope even on price, verification reuse, source immutability, invalid/extra/duplicate query rejection, and the fixed document route. Two new React tests exercise stack selection, real context/priority query changes, abstention, stale-result removal, retry and navigation to the full comparator. Full test suite: 75 Python + 11 UI, no skips; build and Ruff pass.

Connected Chrome confirms the $24 delivery-history choice, $18 price-only choice with unknown history, and pickup abstention after choosing price. A stack layer selects with Space and retains a visible focus ring. New concept views were inspected at normal desktop, 390×844 and 320×844; document widths were 375px and 305px respectively, with no page overflow. Temporary viewport overrides were reset. New screenshots are `docs/screenshots/business-concept-desktop.png` and `docs/screenshots/business-context-mobile.png`. This focused QA does not replace broader accessibility or participant testing.

The refreshed official-source audit completed with `reviewed_snapshot_unchanged`. The immutable UCP v2026-08-25 tree includes location schemas/specs; no new location/business-first UCP extension was emitted. Real candidate coverage, brand/branch identity, serviceability, agent adoption, source truth and consumer/competition gains remain unproven. The current loopback app is a synthetic scope canary, not a global index.
