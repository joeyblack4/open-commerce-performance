import { Button, Modal } from "@heroui/react";
import { date, labels, rate, type Evidence } from "./types";

export function EvidenceDialog({
  evidence,
  merchant,
  close,
}: {
  evidence: Evidence;
  merchant: string;
  close: () => void;
}) {
  const s = evidence.statement,
    m = s.metric,
    v = evidence.verification;
  return (
    <Modal.Backdrop isOpen onOpenChange={(open) => !open && close()}>
      <Modal.Container>
        <Modal.Dialog>
          <Modal.CloseTrigger />
          <Modal.Header>
            <p className="eyebrow">{merchant} · fictional evidence</p>
            <Modal.Heading>{labels[m.id]}</Modal.Heading>
          </Modal.Header>
          <Modal.Body>
            <div className="evidence-head">
              <strong className="number">{rate(m)}</strong>
              <span>
                {m.value === null
                  ? m.status.replaceAll("_", " ")
                  : `${m.numerator} of ${m.denominator} orders`}
              </span>
            </div>
            <p>
              {m.id === "fulfilled_on_time_rate"
                ? "An order counts only when every committed item was delivered by the original checkout promise."
                : m.id === "order_complete_rate"
                  ? "Items and quantities matched the original order at recorded fulfillment. This does not establish doorstep delivery."
                  : "At least one settled refund within 60 days, counted once per order. A refund is not a product defect; low refunds can reflect restrictive policies."}
            </p>
            <dl className="evidence-summary">
              <dt>Historical orders</dt>
              <dd>
                {date(s.period.start)}–{date(s.period.end)} (end exclusive)
              </dd>
              <dt>Observed / expires</dt>
              <dd>
                {date(s.observed_at)} / {date(s.expires_at)}
              </dd>
              <dt>Signal coverage</dt>
              <dd>
                {m.coverage_fraction === null
                  ? "Unavailable or suppressed"
                  : `${Math.round(m.coverage_fraction * 100)}% of eligible orders`}
              </dd>
              <dt>Scope</dt>
              <dd>
                Merchant operations · {s.comparison.country} ·{" "}
                {s.comparison.channel} · {s.comparison.service} service
              </dd>
              <dt>Where it came from</dt>
              <dd>
                Generated fixture orders. Checkout promises and delivery events
                are separate synthetic sources. No real Shopify, carrier or
                merchant connection.
              </dd>
              <dt>Signed origin</dt>
              <dd>
                {v.signature_valid
                  ? "JWS signature valid for the explicitly configured local issuer."
                  : "Signature unavailable or invalid."}
              </dd>
              <dt>Current permission</dt>
              <dd>
                {v.current
                  ? "Current under the simulated clock and consent/status record."
                  : "Not current; cannot support a recommendation."}
              </dd>
              <dt>Calculation</dt>
              <dd>
                {v.arithmetic_consistent
                  ? "Counts and fraction are internally consistent."
                  : "Not established."}{" "}
                {v.calculation_reproduced
                  ? "The local publisher also recomputed the fixture."
                  : "Private source recomputation is unavailable."}
              </dd>
              <dt>Independent truth</dt>
              <dd>
                Not established. No independent source authentication, carrier
                corroboration or audit.
              </dd>
              <dt>Refund policy</dt>
              <dd>
                {s.refund_policy.id.replaceAll("-", " ")}; policies must match
                before comparing refund incidence.
              </dd>
              <dt>Issuer / incentives</dt>
              <dd>
                Black 4 fixture issuer. Local research; no placement or
                affiliate payments.
              </dd>
            </dl>
            <details>
              <summary>Developer statement and JWS</summary>
              <pre>{JSON.stringify(evidence, null, 2)}</pre>
            </details>
          </Modal.Body>
          <Modal.Footer>
            <Button onPress={close}>Done</Button>
          </Modal.Footer>
        </Modal.Dialog>
      </Modal.Container>
    </Modal.Backdrop>
  );
}
