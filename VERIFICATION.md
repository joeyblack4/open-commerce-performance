# Local verification — 2026-10-25

Owning repository: private `joeyblack4/open-commerce-performance`. Branch: `codex/local-synthetic-prototype`. Implementation remains synthetic and loopback-only. No public release, deployed endpoint, actual merchant access or upstream submission.

## Executed checks

| Command | Result |
|---|---|
| `uv sync --frozen` | Locked environment available; runtime cryptography/jsonschema/joserfc installed |
| `npm ci --ignore-scripts` / initial install | Dependency lock produced; final audit below clean |
| `npm test` | **58 tests passed**, 0 skipped, about 8.5 seconds |
| `uv run ruff check src tests scripts` | Passed |
| `uv run ruff format --check src tests scripts` | Passed after formatting one new future-expiry regression |
| `npm run build` | TypeScript and Vite passed; upstream HeroUI `use client` directive notices during bundling |
| `npm audit` | **0 vulnerabilities** after updating Vite to 7.3.7 |
| `PYTHONPATH=src uv run python -m ocp.interop` | Passed offline pinned-schema/fixture intersection; base products unchanged |
| `npm run evaluate` | 12 deterministic scenario/arm cases; no selected offer violated hard price/availability constraints |
| `./scripts/protocol_audit --output artifacts/final-protocol-audit.json` | Network complete; reviewed upstream baseline unchanged |
| `git diff --check` | Passed |

Final protocol check: `2026-10-25T18:42:44.049979-07:00`; snapshot SHA256 `884807323c2e048e534ddb3de3f83b9dd38607f6b52a409a48c9b4be17e039dd`. The first dated audit is tracked in docs/upstream; final runtime logs/screenshot are local ignored artifacts. No platform/MDW code changed, so their monorepo suites/deployment gates were not run in this independent repository.

## Actual consumer and human path

Restarted the implementation server at `http://127.0.0.1:8787` on final source with explicit fixture clock `2026-10-25T20:00:00Z`. Separate consumer bootstrapped public fixture keys/status authority into a new explicit trust file and independently verified all nine JWS envelopes without issuer verifier/decision endpoints.

| Shopper condition | Independent consumer and Chrome result |
|---|---|
| Delivery history preference ≥85%, budget ≤$25 | A ($24): 900/1000 historical on-time/in-full |
| Price first, budget ≤$21 | C ($18), with delivery evidence still unknown |
| Delivery preference, under $20 | Abstained; missing evidence did not label C unreliable |
| Retrieved payload tamper, withdrawn consent or stale status injections | No current evidence; delivery abstention |
| Consumer clock `2027-01-01T00:00:00Z` | Expired fixture rejected; delivery abstention |

Connected Chrome desktop verified synthetic clock, load completion, changed preference choices, readable claim/cohort/source/status/issuer inspector, collapsed developer JWS disclosure, Escape dismissal and focus return. Screenshot: `artifacts/shopper-desktop.png`. The browser's loading state was observed on reload. API tests cover withdrawal/empty public bundles, server refusals and consumer failures.

**Not visually verified:** narrow/mobile viewport, rendered network-error/empty screen, reduced-motion settings and every keyboard sequence. Responsive CSS and native HeroUI behavior are present, but these remaining UI states must not be called proven. This does not limit the demonstrated desktop path or replace future UI acceptance before deployment.

## Adversarial coverage and limits

Tests reject duplicate/nonfinite/oversized JSON, false arithmetic/population counts, source ledger contradictions, wrong subjects/issuers/tenants, sparse diagnostic/outcome leaks, unknown protocol versions, authority confusion, unsupported/critical/key-URL JOSE headers, algorithm substitution and duplicate protected headers. They cover immutable-promise conflicts, incomplete lines/substitution, missing delivery vs fulfillment, cancellation retention, refund maturity/boundaries/deduplication, source omissions, revocation, signed status TTL/digest, key rotation, future expiry and validly signed internally consistent claims failing source recomputation.

Node crypto verifies Python/ joserfc JWS signing inputs, and joserfc verifies a Node-generated signature. That proves framing/key interoperability, not status authority independence or input truth. The consumer cannot reproduce private source records. No real consumer, LLM, carrier, merchant or independent auditor validation occurred. Deterministic scenario agreement is regression evidence, not a blinded utility experiment or measured commerce improvement.

Private branch backup and a private draft PR are owned by the coordinating chat after this clean commit. No second push/PR is created by this implementation chat.
