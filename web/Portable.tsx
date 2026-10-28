import { useEffect, useState } from "react";
import { Button, Modal, Spinner } from "@heroui/react";
import { request } from "./api";
import { hosted, resource, repository } from "./hosting";

const businesses = {
  restaurant: {
    label: "Restaurant",
    name: "Juniper Kitchen",
    metrics: ["pickup", "net-check"],
    situation:
      "You have a short lunch break. A creator's rave about a restaurant doesn't tell you how long its pickup orders take to prepare.",
  },
  ecommerce: {
    label: "Ecommerce brand",
    name: "Fieldwork Goods",
    metrics: ["delivery", "dispatch"],
    situation:
      "You need an order before a birthday. An affiliate list of best brands doesn't tell you how often a retailer meets its original delivery promises.",
  },
  b2b: {
    label: "B2B services",
    name: "Northline Services",
    metrics: ["response", "quote"],
    situation:
      "You need help when work stops. A sponsored comparison doesn't show how long customers waited for a human reply.",
  },
};
const names: Record<string, string> = {
  pickup: "Average pickup preparation time",
  "net-check": "Average net check",
  delivery: "Delivered by the original promise",
  dispatch: "Average time to dispatch",
  response: "Average first human response",
  quote: "Final invoices within the accepted quote",
};
const needNames: Record<string, string> = {
  pickup: "A quick lunch pickup",
  "net-check": "Understand typical check spending",
  delivery: "A dependable delivery history",
  dispatch: "Orders dispatched within a day on average",
  response: "Responsive customer support",
  quote: "Invoices consistent with accepted quotes",
};
type Business = keyof typeof businesses;
type Evidence = {
  metric: string;
  claim: {
    claim_id: string;
    issuer: { name: string; relationship: string };
    method: { id: string; version: string; sha256: string };
    population: {
      start: string;
      end: string;
      eligibility: string;
      exclusions: string[];
      eligible_count: number;
      observed_count: number;
      missing_count: number;
    };
    result: { value: number | null; unit: string; state: string };
    assurance: {
      source_name: string;
      kind: string;
      provider_endorsed: boolean;
    };
    observed_at: string;
    expires_at: string;
    limitations: string[];
  };
  verification: {
    usable: boolean;
    signature_valid: boolean;
    current: boolean;
    source_truth: string;
  };
  publisher_reproduced: boolean;
};
export type PortableResult = {
  business_id: string;
  business: { source: string; needs: { id: string; label: string }[] };
  evidence: Evidence[];
  state: string;
  available: {
    id: string;
    definition: { population: string; limit: string };
  }[];
  assessment: {
    state: string;
    need: string;
    cited_claims: string[];
    threshold: number;
    unknowns: string;
  };
};
function value(e: Evidence) {
  const v = e.claim.result.value;
  if (v === null) return "Unknown";
  if (e.metric === "net-check") return `$${(v / 100).toFixed(2)} per check`;
  if (["delivery", "quote"].includes(e.metric))
    return `${Math.round(v * 100)}%`;
  return `${v.toFixed(1)} ${e.metric === "dispatch" ? "hours" : "minutes"}`;
}

export function Portable() {
  const [business, setBusiness] = useState<Business>("restaurant");
  const [selected, setSelected] = useState<string[]>(["pickup"]);
  const [need, setNeed] = useState("pickup");
  const [state, setState] = useState("published");
  const [result, setResult] = useState<PortableResult | null>(null);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [inspect, setInspect] = useState<Evidence | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    setResult(null);
    setError(false);
    setInspect(null);
    const query = new URLSearchParams({
      business,
      claims: selected.join(",") || "none",
      state,
      need,
    });
    request<PortableResult>(`/v0/portable-preview?${query}`, controller.signal)
      .then((data) => {
        if (!Array.isArray(data.evidence) || data.business_id !== business)
          throw new Error("Invalid preview");
        if (!controller.signal.aborted) setResult(data);
      })
      .catch(() => {
        if (!controller.signal.aborted) setError(true);
      });
    return () => controller.abort();
  }, [business, selected, state, need, retry]);
  function choose(id: Business) {
    setBusiness(id);
    setSelected([businesses[id].metrics[0]]);
    setNeed(businesses[id].metrics[0]);
    setState("published");
  }
  const cited = result?.evidence.find((e) =>
    result.assessment.cited_claims.includes(e.claim.claim_id),
  );
  return (
    <>
      <div className="page-heading portable-intro">
        <p className="eyebrow">
          An open proposal for systems of record and AI platforms
        </p>
        <h1>Recommendations should serve the buyer.</h1>
        <p className="portable-promise">
          Ads, affiliate commissions and sponsored endorsements can shape what
          people discover. When the recommendation fails, the consumer pays in
          money, time and frustration.
        </p>
        <p>
          Give businesses a way to make their service record count. Give AI
          evidence it can check before recommending them.
        </p>
        <div className="button-row">
          <a href={resource("brief")}>Read the proposal (PDF)</a>
          <a href={resource("concept")} download>
            Read the concept
          </a>
          {hosted && <a href={repository}>Explore the repo</a>}
        </div>
      </div>
      <section className="portable-problem" aria-labelledby="problem-heading">
        <h2 id="problem-heading">
          The incentives behind a recommendation matter.
        </h2>
        <dl className="discovery-incentives">
          <div>
            <dt>Paid placement</dt>
            <dd>
              A business can buy visibility without establishing that it meets
              this buyer's needs.
            </dd>
          </div>
          <div>
            <dt>Affiliate rankings</dt>
            <dd>
              A recommender can earn a commission for a sale. That incentive
              says little about delivery, service or total cost.
            </dd>
          </div>
          <div>
            <dt>Sponsored influence</dt>
            <dd>
              A persuasive endorsement or one person's experience cannot
              establish what customers generally receive.
            </dd>
          </div>
        </dl>
        <p>
          The buyer risks the late order, the wasted lunch break or the
          unexpected bill. A business that delivers dependable service still
          needs a way to make that performance visible.
        </p>
        <p className="meta">
          These are incentive risks, not a claim that every recommendation is
          compromised. Read the{" "}
          <a
            href={`${repository}/blob/main/docs/BUSINESS_DISCOVERY_CONCEPT.md#the-problem-with-todays-discovery`}
          >
            research and documented cases
          </a>
          .
        </p>
      </section>
      <section
        className="portable-explanation"
        aria-labelledby="proposal-heading"
      >
        <h2 id="proposal-heading">
          Make business performance usable in discovery.
        </h2>
        <p className="portable-promise">
          Portable evidence about a business that an agent can consult during
          discovery and selection.
        </p>
        <p>
          Businesses choose what to publish. A system of record or named service
          attests to a defined calculation. An agent checks the evidence and
          explains whether it matters to this buyer.
        </p>
      </section>
      <section aria-labelledby="try-heading">
        <div className="section-title">
          <h2 id="try-heading">
            Follow a real buying question through the fictional demo.
          </h2>
        </div>
        <p className="portable-situation">{businesses[business].situation}</p>
        <div className="button-row" role="group" aria-label="Business example">
          {(Object.keys(businesses) as Business[]).map((id) => (
            <Button
              key={id}
              variant={id === business ? "primary" : "secondary"}
              aria-pressed={id === business}
              onPress={() => choose(id)}
            >
              {businesses[id].label}
            </Button>
          ))}
        </div>
        <div className="portable-workspace">
          <section
            className="portable-choices"
            aria-labelledby="publish-heading"
          >
            <p className="eyebrow">1 · The business chooses</p>
            <h2 id="publish-heading">
              What should {businesses[business].name} share?
            </h2>
            <p>
              Choose either measure, both, or neither. This changes a fictional
              preview only.
            </p>
            <div className="stack" role="group" aria-label="Metrics to publish">
              {businesses[business].metrics.map((id) => (
                <Button
                  key={id}
                  variant={selected.includes(id) ? "primary" : "secondary"}
                  aria-pressed={selected.includes(id)}
                  onPress={() =>
                    setSelected((old) =>
                      old.includes(id)
                        ? old.filter((x) => x !== id)
                        : [...old, id],
                    )
                  }
                >
                  {names[id]}
                </Button>
              ))}
            </div>
            <p className="meta">
              Choosing a metric keeps its defined population intact. You cannot
              remove individual unfavorable records.
            </p>
            <h3 className="spaced-heading">Preview the publication status</h3>
            <div
              className="button-row"
              role="group"
              aria-label="Publication status preview"
            >
              {["published", "withdrawn", "disputed"].map((s) => (
                <Button
                  key={s}
                  size="sm"
                  variant={state === s ? "primary" : "secondary"}
                  aria-pressed={state === s}
                  onPress={() => setState(s)}
                >
                  {s[0].toUpperCase() + s.slice(1)}
                </Button>
              ))}
            </div>
          </section>
          <section
            className="publication-preview portable-publication"
            aria-labelledby="claim-heading"
            aria-live="polite"
            aria-busy={!result && !error}
          >
            <p className="eyebrow">2 · A named issuer attests</p>
            <h2 id="claim-heading">The portable evidence</h2>
            {error ? (
              <div role="alert">
                <p>
                  The evidence could not be checked. No previous result is
                  retained.
                </p>
                <Button onPress={() => setRetry((n) => n + 1)}>
                  Retry evidence preview
                </Button>
              </div>
            ) : !result ? (
              <p role="status">
                <Spinner size="sm" /> Calculating and checking the fictional
                claims…
              </p>
            ) : !result.evidence.length ? (
              <div role="status">
                <h3>No metrics selected.</h3>
                <p>
                  This business remains a candidate. Its performance on these
                  measures is unknown.
                </p>
              </div>
            ) : (
              <>
                {state !== "published" && (
                  <p className="portable-status" role="status">
                    {state === "withdrawn"
                      ? "Publication withdrawn"
                      : "Publication disputed"}
                    . These claims cannot support the assessment.
                  </p>
                )}
                {result.evidence.map((e) => (
                  <article className="portable-claim" key={e.metric}>
                    <h3>{names[e.metric]}</h3>
                    <p className="offer-fact">
                      {e.verification.usable
                        ? value(e)
                        : "Unavailable for assessment"}
                    </p>
                    <p>
                      {e.claim.population.observed_count} of{" "}
                      {e.claim.population.eligible_count} eligible records
                      observed · {e.claim.population.missing_count} missing
                    </p>
                    <p className="meta">
                      October 1–24, 2026 · {e.claim.assurance.source_name}
                    </p>
                    <p className="meta">
                      {e.verification.usable
                        ? hosted
                          ? "Signature and status checked at export’s simulated time"
                          : "Local signature and current status checked"
                        : "Current use not established"}
                      . Source accuracy unestablished.
                    </p>
                    <Button
                      size="sm"
                      variant="secondary"
                      onPress={() => setInspect(e)}
                    >
                      Inspect {names[e.metric].toLowerCase()}
                    </Button>
                  </article>
                ))}
                <p className="meta">
                  Issuer: Fictional evidence service. No source provider
                  endorsement. Private records are not in the published claim.
                </p>
              </>
            )}
          </section>
        </div>
      </section>
      <section className="portable-assessment" aria-labelledby="agent-heading">
        <p className="eyebrow">3 · The agent interprets</p>
        <h2 id="agent-heading">What does this buyer care about?</h2>
        <div className="button-row" role="group" aria-label="Buyer need">
          {businesses[business].metrics.map((id) => (
            <Button
              key={id}
              variant={need === id ? "primary" : "secondary"}
              aria-pressed={need === id}
              onPress={() => setNeed(id)}
            >
              {needNames[id]}
            </Button>
          ))}
        </div>
        <div aria-live="polite">
          {!result ? (
            <p>
              {error
                ? "No assessment is available until evidence can be checked."
                : "Checking the evidence for this need…"}
            </p>
          ) : result.assessment.state === "supports_consideration" && cited ? (
            <>
              <h3 className="portable-verdict">
                This record supports considering {businesses[business].name}.
              </h3>
              <p>
                {names[cited.metric]}: <strong>{value(cited)}</strong>.{" "}
                {cited.metric === "net-check"
                  ? "That is below the example's $30 average-check preference. It does not establish a meal price per person."
                  : `That meets this example's ${["delivery", "quote"].includes(cited.metric) ? `${result.assessment.threshold * 100}% minimum historical rate` : `${result.assessment.threshold} ${cited.metric === "dispatch" ? "hour" : "minute"} average-time preference`}.`}
              </p>
              <p>{cited.claim.limitations[0]}</p>
              <p className="meta">
                Evidence citation:{" "}
                <button
                  className="claim-citation"
                  onClick={() => setInspect(cited)}
                >
                  {cited.claim.claim_id}
                </button>
              </p>
            </>
          ) : (
            <>
              <h3 className="portable-verdict">
                {result.assessment.state === "not_supported"
                  ? "The published record does not meet this requirement."
                  : "There is no usable published evidence for this requirement."}
              </h3>
              <p>
                {result.assessment.state === "not_supported"
                  ? "The observed result does not meet this example's threshold."
                  : "The relevant metric is unpublished, unknown, expired, withdrawn or disputed. That does not establish poor performance."}
              </p>
            </>
          )}
          {result && (
            <p>
              <strong>Still unanswered:</strong> {result.assessment.unknowns}
            </p>
          )}
        </div>
        <p className="meta">
          Visible example rules, generated records and three seeded businesses.
          No live AI, market search or future-outcome guarantee.
        </p>
      </section>
      <section
        className="portable-accountability"
        aria-labelledby="accountability-heading"
      >
        <h2 id="accountability-heading">
          The recommendation needs accountability too.
        </h2>
        <p>
          AI platforms must keep paid placement and affiliate incentives separate
          from their assessment of what fits the buyer. They should disclose
          commercial relationships, cite the evidence that mattered and keep
          businesses eligible when they offer no commission.
        </p>
        <p>
          A signature cannot enforce those commitments. Open evidence only helps
          if agents consider it and consumers can challenge the result. The pilot
          must test better service outcomes, participation costs and exposure for
          smaller businesses.
        </p>
        <p className="meta">
          Proposed platform commitments. This demo has no advertising or
          commission inputs and does not test real platform incentives.
        </p>
      </section>
      <section className="two-columns portable-context">
        <div>
          <h2>Where this fits</h2>
          <p>
            Search, maps and directories find businesses. Portable evidence
            helps an agent assess them. Existing commerce protocols carry the
            resulting transaction.
          </p>
          <p>
            The evidence travels with the responsible business or location. Many
            source providers, issuers and agents can participate.
          </p>
        </div>
        <div>
          <h2>A common format, with room for new metrics</h2>
          <p>
            Standardize meaning, scope, issuer and status. Providers and
            industries can define useful measures. Businesses decide what to
            share.
          </p>
          <p>
            Missing evidence stays unknown. Comparable methods support
            comparisons. There is no universal score. Payment must not improve
            an agent's assessment of the same evidence.
          </p>
        </div>
      </section>
      <section className="contribution-note">
        <h2>Build this with systems of record and AI platforms</h2>
        <p>
          The first ask: nominate a product and technical owner, identify one
          native measure your system can responsibly support, and test portable
          claims with independent agents. Help businesses compete through service
          they can substantiate.
        </p>
        <div className="button-row">
          <a href={resource("brief")}>Executive brief</a>
          <a href={resource("protocol")} download>
            Protocol proposal
          </a>
          <a href={resource("schema")}>Candidate claim schema</a>
        </div>
      </section>
      {inspect && (
        <Modal.Backdrop
          isOpen
          onOpenChange={(open) => !open && setInspect(null)}
        >
          <Modal.Container>
            <Modal.Dialog>
              <Modal.CloseTrigger />
              <Modal.Header>
                <Modal.Heading>{names[inspect.metric]}</Modal.Heading>
              </Modal.Header>
              <Modal.Body>
                <p>
                  <strong>{value(inspect)}</strong> · snapshot for this preview
                </p>
                <p>{inspect.claim.population.eligibility}</p>
                <p>
                  Excluded: {inspect.claim.population.exclusions.join(", ")}.{" "}
                  {inspect.claim.population.observed_count} observed /{" "}
                  {inspect.claim.population.eligible_count} eligible;{" "}
                  {inspect.claim.population.missing_count} missing.
                </p>
                <p>
                  Observed October 25, 2026. Expires November 1, 2026. The local
                  clock is explicitly simulated.
                </p>
                <p>
                  <strong>{inspect.claim.issuer.name}</strong>.{" "}
                  {inspect.claim.issuer.relationship}
                </p>
                <p>
                  Publisher calculation reproduced:{" "}
                  {inspect.publisher_reproduced
                    ? "yes, on its own generated records"
                    : "no"}
                  .{" "}
                  {hosted
                    ? "Recorded signature check"
                    : "Consumer signature check"}
                  : {inspect.verification.signature_valid ? "passed" : "failed"}
                  . Status at the simulated clock:{" "}
                  {inspect.verification.current ? "usable" : "not usable"}.
                </p>
                <p>Source accuracy and independent audit are unestablished.</p>
                {inspect.claim.limitations.map((text) => (
                  <p key={text}>{text}</p>
                ))}
                <details>
                  <summary>Method and signed claim</summary>
                  <pre className="code-block">
                    {JSON.stringify(inspect, null, 2)}
                  </pre>
                </details>
              </Modal.Body>
              <Modal.Footer>
                <Button onPress={() => setInspect(null)}>Done</Button>
              </Modal.Footer>
            </Modal.Dialog>
          </Modal.Container>
        </Modal.Backdrop>
      )}
    </>
  );
}
