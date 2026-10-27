# Public concept deployment

Public hosting was authorized October 27 2026. The repository and proposal are Apache-2.0 with their existing notices. The public demo is hosted at https://joeyblack4.github.io/open-commerce-performance/ and the PDF is at https://joeyblack4.github.io/open-commerce-performance/proposal.pdf.

## What runs publicly

GitHub Pages serves a static Vite build, the proposal and 72 precomputed fictional previews. The Python exporter invokes the same calculator and verifier used locally. It exports only selected aggregates, signed claims/status and public fixture keys. No private keys, source rows, provider clients, customer data, cookies, analytics, account access or write endpoints are deployed.

Checks are recorded at `2026-10-25T20:00:00Z`. They are not current real-world verification. The UI discloses the simulated clock and recorded checks. An expired or withdrawn real feed cannot be made usable by this demonstration.

## Build and deploy

`npm run build:site` type-checks, builds for the `/open-commerce-performance/` path and runs `scripts/export_site.py`. The export requires the complete checked-in PDF and copies only named proposal/schema/license resources plus generated fixtures. `publication.json` records the source commit and every exported file digest.

The pinned GitHub Actions workflow validates pull requests. A push to main runs tests and builds, uploads the static artifact and deploys it through GitHub Pages using the repository's standard Pages/OIDC permissions. There are no deployed application secrets. The local Python server retains loopback restrictions.

To preview the exact hosted build, serve `dist` below the `/open-commerce-performance/` path. Do not run the Pages build as the local Python app's assets: they intentionally use different read paths. Rebuild with `npm run build` for the local runtime.

For rollback, revert the relevant main-branch source commit and let the same workflow redeploy. A GitHub release retains the proposal PDF and a source review archive. Updating the PDF starts from `docs/CEO_BRIEF.md` through `scripts/build_proposal.py` using a Python environment with python-docx, then the document renderer; inspect both rendered pages before replacing the checked-in PDF. CI consumes the reviewed PDF and needs no document renderer.

## Verify the release

Check the Pages workflow and `publication.json` source commit. Open the public site and PDF anonymously. Exercise all three business examples, metric omission, buyer-need changes and withdrawal. Inspect an evidence citation. Confirm desktop and 390px layouts and reset viewport overrides. Download the PDF over HTTPS and verify its digest against the publication manifest. These checks establish publication and fictional behavior, not real source truth or ecosystem adoption.
