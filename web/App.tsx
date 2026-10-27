import { useEffect, useState } from "react";
import { Button, Modal, Spinner } from "@heroui/react";
import { request } from "./api";
import { Shop } from "./Shop";
import { Builders } from "./Builders";
import { Portable } from "./Portable";
import { type Bundle } from "./types";
export function App() {
  const [view, setView] = useState("concept"),
    [bundle, setBundle] = useState<Bundle | null>(null),
    [error, setError] = useState(false),
    [about, setAbout] = useState(false);
  async function load() {
    setError(false);
    setBundle(null);
    try {
      const data = await request<Bundle>("/v0/demo");
      if (!Array.isArray(data.merchants)) throw new Error();
      setBundle(data);
    } catch {
      setError(true);
    }
  }
  useEffect(() => {
    if (view === "shop") void load();
  }, [view]);
  return (
    <main>
      <header className="app-header">
        <a
          className="wordmark"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setView("concept");
          }}
        >
          Open Commerce Performance
        </a>
        <nav aria-label="Explore">
          <Button
            variant={view === "concept" ? "primary" : "tertiary"}
            aria-pressed={view === "concept"}
            onPress={() => setView("concept")}
          >
            Portable evidence
          </Button>
          <Button
            variant={view === "shop" ? "primary" : "tertiary"}
            aria-pressed={view === "shop"}
            onPress={() => setView("shop")}
          >
            Comparison reference
          </Button>
          <Button
            variant={view === "builders" ? "primary" : "tertiary"}
            aria-pressed={view === "builders"}
            onPress={() => setView("builders")}
          >
            For builders
          </Button>
        </nav>
      </header>
      <div className="demo-label">
        <span>
          <i aria-hidden="true" />
          Fictional demo · no real stores or purchases
        </span>
        <Button size="sm" variant="tertiary" onPress={() => setAbout(true)}>
          About the evidence
        </Button>
      </div>
      {view === "concept" ? (
        <Portable />
      ) : view === "builders" ? (
        <Builders />
      ) : error ? (
        <section className="load-state" role="alert">
          <h1>We couldn’t load these options.</h1>
          <p>No recommendation is shown from a failed read.</p>
          <Button onPress={() => void load()}>Try again</Button>
        </section>
      ) : !bundle ? (
        <section className="load-state" role="status">
          <Spinner /> Loading your fictional shopping options…
        </section>
      ) : (
        <>
          {bundle.merchants.every((m) => !m.evidence.length) && (
            <div className="empty-notice" role="status">
              No usable evidence is currently shared. You can still compare
              prices; delivery history stays unknown.
            </div>
          )}
          <Shop bundle={bundle} />
        </>
      )}
      <footer>
        <span>
          Business choice. Portable evidence. Recommendations grounded in
          relevant facts.
        </span>
        <span className="meta">
          Experimental proposal · fictional local reference
        </span>
      </footer>
      {about && (
        <Modal.Backdrop
          isOpen
          onOpenChange={(open) => !open && setAbout(false)}
        >
          <Modal.Container>
            <Modal.Dialog>
              <Modal.CloseTrigger />
              <Modal.Header>
                <Modal.Heading>
                  A fictional example, with real checks.
                </Modal.Heading>
              </Modal.Header>
              <Modal.Body>
                <p>
                  These business examples, source records and outcomes are
                  generated. No actual business, source provider, carrier or
                  customer is connected.
                </p>
                <p>
                  Portable examples: October 1–24, 2026. Earlier comparison:
                  April–June 2026. Observed October 25. Demo clock:{" "}
                  {bundle?.demo_clock ?? "2026-10-25T20:00:00Z"} (explicitly
                  simulated).
                </p>
                <p>
                  JWS signatures prove signed origin. Internal consistency and
                  publisher recomputation are separate checks. Source truth and
                  independent audit are not established.
                </p>
                <p>
                  Explanations follow visible rules using the buyer's stated
                  need and applicable evidence. This is not an LLM evaluation, a
                  delivery guarantee or evidence that any commerce platform uses
                  OCP.
                </p>
              </Modal.Body>
              <Modal.Footer>
                <Button onPress={() => setAbout(false)}>Got it</Button>
              </Modal.Footer>
            </Modal.Dialog>
          </Modal.Container>
        </Modal.Backdrop>
      )}
    </main>
  );
}
