import { useEffect, useState } from "react";
import { Button, Modal, Spinner } from "@heroui/react";
import { request } from "./api";
import { Shop } from "./Shop";
import { Merchant } from "./Merchant";
import { Builders } from "./Builders";
import { type Bundle } from "./types";
export function App() {
  const [view, setView] = useState("shop"),
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
    void load();
  }, []);
  return (
    <main>
      <header className="app-header">
        <a
          className="wordmark"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setView("shop");
          }}
        >
          Open Commerce Performance
        </a>
        <nav aria-label="Explore">
          <Button
            variant={view === "shop" ? "primary" : "tertiary"}
            aria-pressed={view === "shop"}
            onPress={() => setView("shop")}
          >
            Shop
          </Button>
          <Button
            variant={view === "merchant" ? "primary" : "tertiary"}
            aria-pressed={view === "merchant"}
            onPress={() => setView("merchant")}
          >
            For merchants
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
      {view === "merchant" ? (
        <Merchant />
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
        <span>Useful facts. Your priorities. No universal merchant score.</span>
        <span className="meta">Synthetic reference · experimental 0.2.0</span>
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
                  These three merchants, their orders and their outcomes are
                  generated examples. No actual store, carrier or customer is
                  connected.
                </p>
                <p>
                  Historical orders: April–June 2026. Observed October 25. Demo
                  clock: {bundle?.demo_clock ?? "2026-10-25T20:00:00Z"}{" "}
                  (explicitly simulated).
                </p>
                <p>
                  JWS signatures prove signed origin. Internal consistency and
                  publisher recomputation are separate checks. Source truth and
                  independent audit are not established.
                </p>
                <p>
                  Recommendations follow visible rules using budget and optional
                  historical delivery preferences. This is not an LLM
                  evaluation, a delivery guarantee or evidence that any commerce
                  platform uses OCP.
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
