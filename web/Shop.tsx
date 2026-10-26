import { useEffect, useState } from "react";
import { Button, Chip, Label, Slider, Spinner } from "@heroui/react";
import { request } from "./api";
import { EvidenceDialog } from "./Evidence";
import {
  labels,
  offers,
  periodLabel,
  rate,
  type Bundle,
  type Decision,
  type Evidence,
  type Preferences,
} from "./types";

const presets: { name: string; value: Preferences }[] = [
  {
    name: "Delivery first",
    value: { budget: 25, priority: "delivery", threshold: 85, evidence: true },
  },
  {
    name: "Lowest price",
    value: { budget: 21, priority: "price", threshold: 85, evidence: true },
  },
  {
    name: "Tight budget",
    value: { budget: 19, priority: "delivery", threshold: 85, evidence: true },
  },
];
export function Shop({ bundle }: { bundle: Bundle }) {
  const [preferences, setPreferences] = useState<Preferences>(presets[0].value);
  const [decision, setDecision] = useState<Decision | null>(null),
    [error, setError] = useState(false),
    [retry, setRetry] = useState(0);
  const [selected, setSelected] = useState<{
    evidence: Evidence;
    name: string;
  } | null>(null);
  useEffect(() => {
    const abort = new AbortController();
    setDecision(null);
    setError(false);
    const q = new URLSearchParams({
      budget: String(preferences.budget * 100),
      priority: preferences.priority,
      threshold: String(preferences.threshold),
      evidence: preferences.evidence ? "on" : "off",
    });
    request<Decision>(`/v0/recommendation?${q}`, abort.signal)
      .then((result) => {
        if (!abort.signal.aborted) setDecision(result);
      })
      .catch(() => {
        if (!abort.signal.aborted) setError(true);
      });
    return () => abort.abort();
  }, [preferences, retry]);
  const chosen = bundle.merchants.find((m) => m.subject === decision?.choice);
  const chosenPrice = chosen ? offers[chosen.subject] : 0;
  const delta = chosen ? chosenPrice - Math.min(...Object.values(offers)) : 0;
  const change = (value: Partial<Preferences>) =>
    setPreferences((p) => ({ ...p, ...value }));
  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">Same grocery box. Three fictional merchants.</p>
        <h1>Find the delivery that fits you.</h1>
        <p className="lead">
          Set your budget and what matters. See the tradeoff before you choose.
        </p>
      </div>
      <div className="shopping-workspace">
        <section
          className="shopping-brief"
          aria-label="Your shopping preferences"
        >
          <h2>Your priorities</h2>
          <Slider
            aria-label="Total budget"
            value={preferences.budget}
            minValue={15}
            maxValue={30}
            step={1}
            onChange={(v) => change({ budget: Array.isArray(v) ? v[0] : v })}
          >
            <div className="control-label">
              <Label>Total budget</Label>
              <Slider.Output>{`$${preferences.budget}`}</Slider.Output>
            </div>
            <Slider.Track>
              <Slider.Fill />
              <Slider.Thumb />
            </Slider.Track>
          </Slider>
          <div className="range-labels">
            <span>$15</span>
            <span>$30 · delivered total</span>
          </div>
          <div className="control-group">
            <p className="control-title">What matters most?</p>
            <div className="stack" role="group" aria-label="Main priority">
              <Button
                variant={
                  preferences.priority === "delivery" ? "primary" : "secondary"
                }
                aria-pressed={preferences.priority === "delivery"}
                onPress={() => change({ priority: "delivery" })}
              >
                Delivery history
              </Button>
              <Button
                variant={
                  preferences.priority === "price" ? "primary" : "secondary"
                }
                aria-pressed={preferences.priority === "price"}
                onPress={() => change({ priority: "price" })}
              >
                Lowest price
              </Button>
            </div>
          </div>
          {preferences.priority === "delivery" && (
            <details className="brief-options">
              <summary>Delivery requirement: {preferences.threshold}%+</summary>
              <div
                className="button-row"
                role="group"
                aria-label="Historical delivery threshold"
              >
                {[75, 85, 95].map((n) => (
                  <Button
                    size="sm"
                    key={n}
                    variant={
                      n === preferences.threshold ? "primary" : "secondary"
                    }
                    aria-pressed={n === preferences.threshold}
                    onPress={() => change({ threshold: n })}
                  >
                    {n}%+
                  </Button>
                ))}
              </div>
              <p className="meta">
                Your minimum for the historical record. It cannot guarantee this
                delivery.
              </p>
            </details>
          )}
          <a
            className="button button--primary mobile-result-link"
            href="#shop-result"
          >
            See my options
          </a>
        </section>
        <div className="shopping-result" id="shop-result">
          {error ? (
            <div role="alert" className="result-surface">
              <h2>We couldn’t check these options.</h2>
              <p>No recommendation is being shown from a failed read.</p>
              <Button onPress={() => setRetry((n) => n + 1)}>Try again</Button>
            </div>
          ) : !decision ? (
            <div className="result-surface" role="status">
              <Spinner /> Checking your priorities…
            </div>
          ) : (
            <section
              className="result-surface"
              aria-live="polite"
              aria-label="Your result"
            >
              <p className="eyebrow">
                {chosen
                  ? "A fit for your priorities"
                  : "Let’s adjust the brief"}
              </p>
              <div className="result-heading">
                <h2>
                  {chosen?.name ??
                    (decision.state === "no_eligible_offers"
                      ? "Your budget is below these offers."
                      : "We need more evidence to choose.")}
                </h2>
                {chosen && (
                  <span className="price">
                    ${chosenPrice}
                    <small>delivered</small>
                  </span>
                )}
              </div>
              {chosen ? (
                <>
                  <p className="result-reason">
                    {preferences.priority === "price"
                      ? `At $${chosenPrice}, this is the lowest-priced available offer within your $${preferences.budget} budget.`
                      : `${chosen.name} meets your ${preferences.threshold}% historical delivery preference and stays within your $${preferences.budget} budget.`}
                  </p>
                  <div className="tradeoff">
                    <strong>What you’re trading</strong>
                    <p>
                      {preferences.priority === "price"
                        ? "The lowest price comes with unknown delivery history. That’s a gap in evidence, not proof of poor service."
                        : delta > 0
                          ? `You spend $${delta} more than the $18 option to choose a merchant with a qualifying delivery record.`
                          : "This option meets your delivery-history preference at the lowest listed price."}
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <p className="result-reason">
                    {decision.state === "no_eligible_offers"
                      ? "The lowest-priced offer is $18. Increase your budget to include it, or compare a different item."
                      : "The offers in your budget either fall below your historical preference or have no usable delivery evidence. We won’t turn unknowns into a winner."}
                  </p>
                  <div className="button-row">
                    {(decision.adjustments ?? []).map((adjustment) => (
                      <Button
                        key={adjustment.label}
                        variant={
                          adjustment.priority === "price"
                            ? "secondary"
                            : "primary"
                        }
                        onPress={() =>
                          setPreferences({
                            budget: adjustment.budget,
                            priority: adjustment.priority,
                            threshold: adjustment.threshold,
                            evidence: adjustment.evidence,
                          })
                        }
                      >
                        {adjustment.label}
                      </Button>
                    ))}
                  </div>
                </>
              )}
              <p className="meta">
                Historical orders: {periodLabel}. All offers are in stock. This
                rule-based fictional example does not predict arrival or product
                quality.
              </p>
            </section>
          )}
          <section className="offer-list" aria-labelledby="offer-title">
            <div className="section-title">
              <h2 id="offer-title">Your options</h2>
              <span className="meta">
                Identical box · same stock · no paid placement
              </span>
            </div>
            {bundle.merchants.map((merchant) => {
              const assessment = decision?.assessments.find(
                (a) => a.subject === merchant.subject,
              );
              const delivery = merchant.evidence.find(
                (e) => e.statement.metric.id === "fulfilled_on_time_rate",
              );
              const active = decision?.choice === merchant.subject;
              return (
                <article
                  className={`offer-row ${active ? "chosen" : ""}`}
                  key={merchant.subject}
                >
                  <div className="offer-identity">
                    <h3>{merchant.name}</h3>
                    <span className="meta">
                      Fictional merchant · ${offers[merchant.subject]} delivered
                    </span>
                  </div>
                  <div>
                    <span className="offer-fact">
                      {preferences.evidence
                        ? rate(delivery?.statement.metric)
                        : "Unknown"}
                    </span>
                    <span className="meta block">
                      past orders on time & complete
                    </span>
                  </div>
                  <div className="offer-action">
                    <Chip size="sm" variant="soft">
                      {active
                        ? "Fits your brief"
                        : assessment && !assessment.eligible
                          ? "Over budget"
                          : assessment?.historical_on_time === null
                            ? "History unknown"
                            : "Compare the tradeoff"}
                    </Chip>
                    <Button
                      size="sm"
                      variant="tertiary"
                      isDisabled={!delivery}
                      onPress={() =>
                        delivery &&
                        setSelected({ evidence: delivery, name: merchant.name })
                      }
                    >
                      See the evidence
                    </Button>
                  </div>
                </article>
              );
            })}
          </section>
        </div>
      </div>
      <details className="extra-context">
        <summary>Try another brief or compare without shared evidence</summary>
        <div className="button-row">
          {presets.map((p) => (
            <Button
              key={p.name}
              variant="secondary"
              onPress={() => setPreferences(p.value)}
            >
              {p.name}
            </Button>
          ))}
        </div>
        <div className="control-group">
          <Button
            variant="secondary"
            onPress={() => change({ evidence: !preferences.evidence })}
          >
            {preferences.evidence
              ? "Hide operational evidence"
              : "Use operational evidence"}
          </Button>
          <p className="meta">
            Offers, prices and stock stay the same. Unknown history remains
            unknown.
          </p>
        </div>
      </details>
      <details className="extra-context">
        <summary>See all three measures and how the choice works</summary>
        <p>
          The choice uses only your budget and, when requested, the
          delivered-on-time-and-complete history. Refund incidence never acts as
          a low-is-good quality signal.
        </p>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Historical measure</th>
                {bundle.merchants.map((m) => (
                  <th key={m.subject}>{m.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(labels).map(([id, label]) => (
                <tr key={id}>
                  <th>{label}</th>
                  {bundle.merchants.map((m) => {
                    const e = m.evidence.find(
                      (x) => x.statement.metric.id === id,
                    );
                    return (
                      <td key={m.subject}>
                        {rate(e?.statement.metric)}
                        <span className="meta block">
                          {e?.statement.metric.numerator ?? "—"} /{" "}
                          {e?.statement.metric.denominator ?? "—"} orders
                        </span>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="meta">
          Refund policy: returns accepted for 60 days. A refund is not a product
          defect. Completeness at fulfillment is not doorstep delivery.
        </p>
      </details>
      {selected && (
        <EvidenceDialog
          evidence={selected.evidence}
          merchant={selected.name}
          close={() => setSelected(null)}
        />
      )}
    </>
  );
}
