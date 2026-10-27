import { useEffect, useState } from "react";
import { Button, Spinner } from "@heroui/react";
import { request } from "./api";
import { type Decision, offers } from "./types";

const layers = [
  {
    title: "Find relevant businesses",
    owner: "Search, maps, directories and agent indexes",
    text: "Build a candidate set for the consumer’s need. Keep where each candidate came from, which sources were searched and what may be missing. Performance evidence cannot help a business the agent never finds.",
    now: "This demo seeds three fictional merchants. It performs no global search and cannot measure market coverage.",
  },
  {
    title: "Identify the responsible business",
    owner: "Existing business identities and protocol profiles",
    text: "Bind evidence to the seller, branch or service actually responsible. A brand, franchise, marketplace seller and manufacturer are different subjects. A strong result for one must not become a claim about all of them.",
    now: "Three fixed merchant identities are pinned locally. No legal-entity, branch or brand relationships are verified.",
  },
  {
    title: "Check relevant performance evidence",
    owner: "Optional OCP evidence and consumer-side verification",
    text: "Ask what happened, to which population, during which period, according to whom. Verify origin and current status, then check scope, coverage, comparable methods and source assurance. A signature alone cannot establish truth.",
    now: "Signed synthetic aggregates, status and scope checks work. Source authenticity and independent audit remain unestablished.",
  },
  {
    title: "Recommend for this person",
    owner: "The consumer’s agent and stated priorities",
    text: "Compare eligible businesses under the person’s needs, budget and tradeoffs. Explain why the evidence matters. Keep unknown businesses visible and allow an honest abstention. Payment for publication must never purchase a better verdict.",
    now: "Deterministic budget/history rules change the chosen merchant. No LLM or real consumer-outcome study has run.",
  },
  {
    title: "Transact through existing rails",
    owner: "UCP, supported checkout and payment authorization",
    text: "Refresh actual prices, availability, terms and fulfillment promises before a purchase. Use supported commerce capabilities and payment authorization. Evidence about past orders grants no authority to buy and guarantees no future result.",
    now: "An offline UCP catalog extension passes pinned schema tests. No live UCP negotiation, checkout or payment runs.",
  },
  {
    title: "Measure outcomes and permit correction",
    owner: "Consented source systems, verifiers and independent evaluation",
    text: "Compare the promised service with observed outcomes. Preserve provenance, correction and appeal. Measure consumer harm, price, access and business participation—not just recommendation clicks. Feed improvements into later evidence.",
    now: "Withdrawal and dispute previews work locally. Persistent correction, real outcomes and competition effects are future work.",
  },
];
type Discovery = {
  state: string;
  reason: string;
  candidates: { subject: string; name: string; service_fit: string }[];
  decision: Decision | null;
};

export function Concept({ onCompare }: { onCompare: () => void }) {
  const [layer, setLayer] = useState(0);
  const [context, setContext] = useState("shipped-order");
  const [priority, setPriority] = useState("delivery");
  const [result, setResult] = useState<Discovery | null>(null);
  const [error, setError] = useState(false),
    [retry, setRetry] = useState(0);
  useEffect(() => {
    const abort = new AbortController();
    setResult(null);
    setError(false);
    const query = new URLSearchParams({
      context,
      priority,
      budget: "2500",
      threshold: "85",
      evidence: "on",
    });
    request<Discovery>(`/v0/business-discovery?${query}`, abort.signal)
      .then((value) => {
        if (!abort.signal.aborted) setResult(value);
      })
      .catch(() => {
        if (!abort.signal.aborted) setError(true);
      });
    return () => abort.abort();
  }, [context, priority, retry]);
  const chosen = result?.candidates.find(
    (m) => m.subject === result.decision?.choice,
  );
  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">Business discovery and consumer outcomes</p>
        <h1>Help people choose businesses on relevant evidence.</h1>
        <p className="lead">
          Make actual service easier to compare, while keeping the consumer in
          control of what matters.
        </p>
      </div>
      <section aria-labelledby="stack-title">
        <h2 id="stack-title">Where it fits in the commerce stack</h2>
        <p>
          Business discovery finds the candidates. Evidence helps assess them.
          Commerce protocols carry the transaction. Explore each responsibility.
        </p>
        <div className="concept-stack">
          <div
            className="stack"
            role="group"
            aria-label="Commerce stack layers"
          >
            {layers.map((item, index) => (
              <Button
                key={item.title}
                variant={layer === index ? "primary" : "secondary"}
                aria-pressed={layer === index}
                onPress={() => setLayer(index)}
              >
                {index + 1}. {item.title}
              </Button>
            ))}
          </div>
          <section
            className="concept-detail"
            aria-label="Selected stack layer"
            aria-live="polite"
          >
            <p className="eyebrow">{layers[layer].owner}</p>
            <h3>{layers[layer].title}</h3>
            <p>{layers[layer].text}</p>
            <h3>What works here today</h3>
            <p>{layers[layer].now}</p>
          </section>
        </div>
      </section>
      <section className="concept-example" aria-labelledby="scope-title">
        <h2 id="scope-title">Try the boundary: good for which need?</h2>
        <p>
          These are three seeded fictional businesses, not a search of the
          market. The same grocery box holds the product constant so we can
          compare the seller’s service. Budget: $25.
        </p>
        <div
          className="button-row"
          role="group"
          aria-label="Business discovery need"
        >
          {[
            ["shipped-order", "Shipped order"],
            ["local-pickup", "Local pickup"],
            ["prepared-meal", "Meal delivery"],
          ].map(([value, label]) => (
            <Button
              key={value}
              variant={context === value ? "primary" : "secondary"}
              aria-pressed={context === value}
              onPress={() => setContext(value)}
            >
              {label}
            </Button>
          ))}
        </div>
        <div
          className="button-row discovery-priority"
          role="group"
          aria-label="Discovery priority"
        >
          <span>Choose by</span>
          <Button
            variant={priority === "delivery" ? "primary" : "secondary"}
            aria-pressed={priority === "delivery"}
            onPress={() => setPriority("delivery")}
          >
            85%+ delivery history
          </Button>
          <Button
            variant={priority === "price" ? "primary" : "secondary"}
            aria-pressed={priority === "price"}
            onPress={() => setPriority("price")}
          >
            Lowest price
          </Button>
        </div>
        <div className="concept-discovery" aria-live="polite">
          {error ? (
            <div role="alert">
              <h3>We couldn’t assess these businesses.</h3>
              <p>No previous recommendation is retained.</p>
              <Button onPress={() => setRetry((n) => n + 1)}>
                Retry business assessment
              </Button>
            </div>
          ) : !result ? (
            <p role="status">
              <Spinner size="sm" /> Checking the scope of this request…
            </p>
          ) : result.state === "scope_not_established" ? (
            <>
              <h3>We can’t recommend a business for this need.</h3>
              <p>{result.reason}</p>
              <p>
                The three candidates stay known; their eligibility and relevant
                performance remain unknown. Switching to price cannot supply
                missing service evidence.
              </p>
            </>
          ) : chosen ? (
            <>
              <h3>
                {chosen.name} fits this brief · ${offers[chosen.subject]}
              </h3>
              <p>
                {priority === "price"
                  ? "The lowest-price fictional merchant wins. Its delivery history stays unknown; lack of published evidence is not poor performance."
                  : "900 of 1,000 historical orders were on time and complete. That meets this shopper’s 85% preference at $6 above the lowest price. It does not establish pickup performance or product quality."}
              </p>
              <p>
                A different consumer can rationally choose a different business.
                There is no overall winner.
              </p>
            </>
          ) : (
            <>
              <h3>There is not enough relevant evidence to choose.</h3>
              <p>{result.decision?.reason}</p>
            </>
          )}
        </div>
        <Button variant="secondary" onPress={onCompare}>
          Explore budgets and inspect the evidence
        </Button>
      </section>
      <section className="two-columns">
        <div>
          <h2>Competition on service people value</h2>
          <p>
            The hypothesis: portable, comparable evidence can help a smaller
            business get considered without buying a favorable recommendation.
            It only helps if the business is found, can afford to participate
            and actually delivers outcomes people value.
          </p>
          <p>
            Candidate coverage and support for new businesses matter as much as
            checking the claims of incumbents. Missing evidence stays unknown.
          </p>
        </div>
        <div>
          <h2>Keep the new gatekeepers accountable</h2>
          <p>
            Publish methods, denominators, funding relationships and correction
            paths. Separate advertisements from evidence-based recommendations.
            Do not sell scores, force a single verifier or transfer a branch’s
            record to an entire brand.
          </p>
          <p>
            Open data alone cannot force an AI platform to use it fairly.
            Adoption, independent evaluation and consumer choice remain
            necessary.
          </p>
        </div>
      </section>
      <section className="contribution-note">
        <h2>The full concept and unresolved questions</h2>
        <p>
          The paper covers global discovery, business and brand identity, UCP
          integration options, source manipulation, cold starts, business
          incentives, privacy and a test plan for actual consumer benefit.
          Broader claims remain proposals, not deployed capabilities.
        </p>
        <a href="/concept.md" download>
          Download the full concept (.md)
        </a>
      </section>
    </>
  );
}
