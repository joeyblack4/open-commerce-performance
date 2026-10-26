# Product verification — 2026-10-25; publication update — 2026-10-26

Repository `joeyblack4/open-commerce-performance`, implemented in PR #1. The owner authorized public distribution under Apache-2.0 on October 26, 2026. Source and synthetic demo only; no live merchant data, production deployment, named outreach or upstream submission.

## Automated checks

| Check | Result |
|---|---|
| Clean `npm ci --ignore-scripts` using the locked dependencies | Passed; standard npm installation works |
| `npm test` | **69 Python tests + 9 React UI tests passed**, no skips |
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
