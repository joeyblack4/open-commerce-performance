import { useEffect, useState } from "react";
import { Button, Chip, Spinner } from "@heroui/react";
import { request } from "./api";
import { EvidenceDialog } from "./Evidence";
import {
  labels,
  periodLabel,
  rate,
  type Evidence,
  type MerchantPreview,
} from "./types";

export function Merchant() {
  const [state, setState] = useState("shared"),
    [preview, setPreview] = useState<MerchantPreview | null>(null);
  const [error, setError] = useState(false),
    [retry, setRetry] = useState(0),
    [selected, setSelected] = useState<Evidence | null>(null);
  useEffect(() => {
    const abort = new AbortController();
    setPreview(null);
    setError(false);
    request<MerchantPreview>(
      `/v0/merchant-preview?state=${state}`,
      abort.signal,
    )
      .then((result) => {
        if (!abort.signal.aborted) setPreview(result);
      })
      .catch(() => {
        if (!abort.signal.aborted) setError(true);
      });
    return () => abort.abort();
  }, [state, retry]);
  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">For merchants</p>
        <h1>Let shoppers see the service you deliver.</h1>
        <p className="lead">
          Share useful operational facts voluntarily. Shoppers decide what
          matters to them.
        </p>
      </div>
      <div className="merchant-intro">
        <p>
          <strong>A practical reason to participate</strong>
          <br />
          If delivery reliability is your strength, a price-only comparison can
          miss it. Shared evidence can make that tradeoff visible to a shopper
          or their agent.
        </p>
        <p className="meta">
          That is a hypothesis to test—not a sales-lift promise, paid ranking
          advantage or guaranteed placement in an AI platform.
        </p>
      </div>
      <section
        className="merchant-workspace"
        aria-label="Fictional publication preview"
      >
        <div className="preview-controls">
          <p className="eyebrow">Interactive example · Cedar Market</p>
          <h2>Preview what you share.</h2>
          <p>
            This changes a private simulation only. No store is connected and no
            publication or consent record is changed.
          </p>
          <div
            className="stack"
            role="group"
            aria-label="Publication preview state"
          >
            <Button
              variant={state === "shared" ? "primary" : "secondary"}
              aria-pressed={state === "shared"}
              onPress={() => setState("shared")}
            >
              Sharing the full bundle
            </Button>
            <Button
              variant={state === "withdrawn" ? "primary" : "secondary"}
              aria-pressed={state === "withdrawn"}
              onPress={() => setState("withdrawn")}
            >
              Preview withdrawal
            </Button>
            <Button
              variant={state === "disputed" ? "primary" : "secondary"}
              aria-pressed={state === "disputed"}
              onPress={() => setState("disputed")}
            >
              Preview a disputed record
            </Button>
          </div>
          <p className="meta">
            The bundle includes all three measures. You cannot hide only an
            unfavorable measure to improve this preview.
          </p>
        </div>
        <div className="publication-preview">
          {error ? (
            <div role="alert">
              <h2>The preview could not load.</h2>
              <Button onPress={() => setRetry((n) => n + 1)}>
                Retry preview
              </Button>
            </div>
          ) : !preview ? (
            <div role="status">
              <Spinner /> Preparing the publication preview…
            </div>
          ) : (
            <>
              <div className="section-title">
                <h2>What a shopper could read</h2>
                <Chip size="sm" variant="soft">
                  {state === "shared"
                    ? "Shared · fictional"
                    : state === "withdrawn"
                      ? "Withdrawn in preview"
                      : "Disputed in preview"}
                </Chip>
              </div>
              {preview.merchant.evidence.length ? (
                <>
                  <p className="meta">
                    Fixed {periodLabel} cohort · aggregate figures only
                  </p>
                  {preview.merchant.evidence.map((e) => (
                    <div
                      className="published-measure"
                      key={e.statement.metric.id}
                    >
                      <div>
                        <h3>{labels[e.statement.metric.id]}</h3>
                        <p className="meta">
                          {e.statement.metric.numerator} /{" "}
                          {e.statement.metric.denominator} orders ·{" "}
                          {Math.round(
                            (e.statement.metric.coverage_fraction ?? 0) * 100,
                          )}
                          % signal coverage
                        </p>
                      </div>
                      <strong>{rate(e.statement.metric)}</strong>
                      <Button
                        size="sm"
                        variant="tertiary"
                        onPress={() => setSelected(e)}
                      >
                        Inspect
                      </Button>
                    </div>
                  ))}
                  <p className="meta">
                    Refund policy travels with refund incidence. Lower refunds
                    do not automatically mean better products or service.
                  </p>
                </>
              ) : (
                <div className="withdrawal-state" role="status">
                  <h3>
                    {state === "withdrawn"
                      ? "These claims no longer support a recommendation."
                      : "A disputed claim should not decide the purchase."}
                  </h3>
                  <p>
                    {state === "withdrawn"
                      ? "The same signed bytes may still exist in a cache. Current consent and status checks reject them, and the shopper sees no usable evidence."
                      : "The status model blocks definitive use while the record is disputed. Correction means a new reviewed statement and a supersession link, not a silent edit."}
                  </p>
                  <p>
                    Absence of usable evidence does not label your business
                    unreliable.
                  </p>
                </div>
              )}
              <details>
                <summary>See the status checks behind this preview</summary>
                <p>
                  These checks use the actual local signature and status
                  verifier on a separate in-memory projection.
                </p>
                <pre>{JSON.stringify(preview.status_checks, null, 2)}</pre>
              </details>
            </>
          )}
        </div>
      </section>
      <section className="merchant-explainer" aria-labelledby="data-title">
        <h2 id="data-title">What the evidence needs</h2>
        <div className="source-matrix">
          <div>
            <h3>Order and refund records</h3>
            <p>
              Authorized order history, exact item quantities, a complete
              population and settled-refund events. A mature 60-day refund
              cohort needs sufficient history.
            </p>
            <Chip size="sm" variant="soft">
              Read access and coverage required
            </Chip>
          </div>
          <div>
            <h3>Original promise + actual delivery</h3>
            <p>
              An immutable checkout promise and separately sourced final
              delivery. Marking an order fulfilled is not proof that it arrived.
            </p>
            <Chip size="sm" variant="soft">
              Additional evidence required
            </Chip>
          </div>
          <div>
            <h3>Product quality and repeat purchases</h3>
            <p>
              Delivery and refunds do not establish durability or satisfaction.
              Product reliability and voluntary repeat purchases are outside
              this prototype.
            </p>
            <Chip size="sm" variant="soft">
              Unsupported here
            </Chip>
          </div>
        </div>
      </section>
      <section className="two-columns">
        <div>
          <h2>What stays private</h2>
          <p>
            No customer names, addresses, emails, order IDs or payment details
            enter the shared statement. Small cohorts and sparse outcomes are
            suppressed.
          </p>
          <p className="meta">
            A cohort threshold is a safeguard, not a complete privacy guarantee.
            Real publication needs a review across the whole bundle.
          </p>
        </div>
        <div>
          <h2>What stays in your control</h2>
          <p>
            Consent to access records is separate from consent to publish
            aggregates. Corrections get a new version. Withdrawal changes
            current status. Verifier relationships are disclosed.
          </p>
          <p className="meta">
            Fees cannot purchase a favorable measure or ranking. No Shopify or
            Square connection is created by this demo.
          </p>
        </div>
      </section>
      {selected && (
        <EvidenceDialog
          evidence={selected}
          merchant="Cedar Market"
          close={() => setSelected(null)}
        />
      )}
    </>
  );
}
