import { useEffect, useState } from "react";
import { request } from "./api";
import { Button } from "@heroui/react";
export function Builders() {
  const [copied, setCopied] = useState(false);
  const [packageReady, setPackageReady] = useState(false);
  useEffect(() => {
    request<{ prepared: boolean }>("/v0/release-info")
      .then((result) => setPackageReady(result.prepared === true))
      .catch(() => setPackageReady(false));
  }, []);
  const quickstart =
    "uv sync --frozen\nnpm ci --ignore-scripts\nnpm run build\nnpm run demo";
  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">For builders</p>
        <h1>Try useful evidence beside the commerce flow.</h1>
        <p className="lead">
          A small reference implementation: signed aggregate facts, explicit
          trust, and a shopper who can say “not enough evidence.”
        </p>
      </div>
      <div className="builder-workspace">
        <section>
          <h2>Run it locally</h2>
          <p>
            Python 3.11+, uv, Node 22.12+ and npm. No merchant account, API key
            or database.
          </p>
          <pre className="code-block">{quickstart}</pre>
          <Button
            variant="secondary"
            onPress={async () => {
              try {
                await navigator.clipboard.writeText(quickstart);
                setCopied(true);
              } catch {
                setCopied(false);
              }
            }}
          >
            {copied ? "Copied" : "Copy commands"}
          </Button>
          <p className="meta">
            Explicit fixture clock: October 25, 2026. Real-time verification
            still rejects expired claims.
          </p>
          <h2 className="spaced-heading">Verify as the consumer</h2>
          <pre className="code-block">
            {
              "PYTHONPATH=src uv run python -m ocp.consumer \\\n  --bootstrap-local --trust artifacts/local-trust.json \\\n  --fixture-as-of 2026-10-25T20:00:00Z \\\n  --budget-cents 2500 --priority delivery --threshold 85"
            }
          </pre>
          <p className="meta">
            Bootstrap explicitly pins this fictional local process. Discovery is
            not trust. Existing pins are never silently replaced.
          </p>
        </section>
        <section>
          <h2>Follow the evidence</h2>
          <ol className="evidence-flow">
            <li>
              <strong>Existing commerce systems</strong>
              <span>
                Keep catalog, checkout, payments and source authority with their
                current owners.
              </span>
            </li>
            <li>
              <strong>Opt-in aggregate resource</strong>
              <span>
                Population, method, counts, coverage, historical window and
                current consent/status.
              </span>
            </li>
            <li>
              <strong>The shopper’s verifier and priorities</strong>
              <span>
                Check JWS, issuer/subject, method and status before interpreting
                the facts. Unknowns can lead to abstention.
              </span>
            </li>
          </ol>
          <div className="link-list">
            <a href="/v0/.well-known/ocp" target="_blank" rel="noreferrer">
              Inspect experimental evidence discovery ↗
            </a>
            <a href="/v0/schema/0.2.0" target="_blank" rel="noreferrer">
              Read the versioned aggregate schema ↗
            </a>
            <a href="/v0/interop" target="_blank" rel="noreferrer">
              Inspect the pinned UCP fixture result ↗
            </a>
            {packageReady ? (
              <a href="/v0/release-package" download>
                Download the review package
              </a>
            ) : (
              <p className="meta">
                Prepare a review archive from a clean committed checkout:{" "}
                <code>npm run package:review</code>.
              </p>
            )}
          </div>
        </section>
      </div>
      <section className="protocol-list" aria-labelledby="protocol-title">
        <h2 id="protocol-title">Where it fits—and where it doesn’t</h2>
        <div>
          <h3>UCP · published 2026-08-25</h3>
          <p>
            An offline vendor-namespaced catalog-reference example validates
            against unchanged pinned schemas. Unsupported clients keep the base
            catalog. The HTTPS fixture URLs are unhosted; this is not a live UCP
            server or certification.
          </p>
        </div>
        <div>
          <h3>ACP · dated source 2026-04-17</h3>
          <p>
            Separate feed and checkout contracts. No undocumented feed fields or
            claim that ChatGPT ingests OCP. The sharing draft asks about an
            accepted enrichment path.
          </p>
        </div>
        <div>
          <h3>AP2 · v0.2.0</h3>
          <p>
            Payment authorization stays with payment protocols. A payment
            mandate or settlement does not establish merchant or product
            quality.
          </p>
        </div>
        <div>
          <h3>Shopify and Square source systems</h3>
          <p>
            Square participates in UCP’s Food Technical Council. This prototype
            makes no claim of OCP adoption by Shopify or Square. This build uses
            synthetic records only. Fulfillment completion and refund update
            timestamps cannot silently become independently verified delivery or
            settlement events.
          </p>
        </div>
      </section>
      <section className="contribution-note">
        <h2>Poppy · adjacent working draft</h2>
        <p>
          The official Personal Agent Protocol docs were observed at Draft 0.3,
          explicitly in progress. They address personal-agent/company discovery
          and authorization/session interaction. This example stays beside that
          layer and adds no authentication or session system.
        </p>
        <p className="meta">
          Deployed docs and public repository version metadata currently differ.
          The audit records both; no Poppy conformance is claimed.
        </p>
      </section>
      <section className="contribution-note">
        <h2>A concrete contribution question</h2>
        <p>
          Should an optional merchant-scoped aggregate-evidence reference extend
          UCP catalog lookup, or remain a separate opt-in resource? The package
          includes runnable base/opt-in fixtures, the threat model,
          missing-source cases and the exact question.
        </p>
        <p className="meta">
          The review package is prepared locally. No company has been contacted,
          no upstream submission made, and no platform endorsement claimed.
        </p>
      </section>
    </>
  );
}
