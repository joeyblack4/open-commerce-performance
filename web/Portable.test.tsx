import React from "react";
import { expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Portable } from "./Portable";

const definitions: Record<
  string,
  { name: string; metrics: string[]; values: number[] }
> = {
  restaurant: {
    name: "Juniper Kitchen",
    metrics: ["pickup", "net-check"],
    values: [14, 2600],
  },
  ecommerce: {
    name: "Fieldwork Goods",
    metrics: ["delivery", "dispatch"],
    values: [0.94, 23],
  },
  b2b: {
    name: "Northline Services",
    metrics: ["response", "quote"],
    values: [28, 0.97],
  },
};
function api(url: string) {
  const q = new URL(url, "http://localhost").searchParams;
  const business = q.get("business")!;
  const b = definitions[business];
  const selected = q.get("claims")!.split(",");
  const state = q.get("state")!;
  const need = q.get("need")!;
  const usable = state === "published";
  const evidence = b.metrics
    .filter((m) => selected.includes(m))
    .map((m) => ({
      metric: m,
      claim: {
        claim_id: `fictional:${business}:${m}`,
        issuer: {
          name: "Fictional evidence service",
          relationship: "No provider endorsement",
        },
        method: {
          id: "https://example.invalid/method",
          version: "0.1.0",
          sha256: "abc",
        },
        population: {
          start: "2026-10-01",
          end: "2026-10-25",
          eligibility: "All eligible fictional records",
          exclusions: ["Test records"],
          eligible_count: 100,
          observed_count: 100,
          missing_count: 0,
        },
        result: {
          value: b.values[b.metrics.indexOf(m)],
          unit: "minutes",
          state: "observed",
        },
        assurance: {
          source_name: "Fictional source",
          provider_endorsed: false,
          kind: "service_calculated",
        },
        limitations: ["Does not establish overall quality."],
      },
      verification: {
        usable,
        signature_valid: true,
        current: usable,
        source_truth: "not_established",
      },
      publisher_reproduced: true,
    }));
  const cited = evidence.find(
    (e) => e.metric === need && e.verification.usable,
  );
  return Promise.resolve(
    new Response(
      JSON.stringify({
        business_id: business,
        business: { source: "Fictional source", needs: [] },
        evidence,
        state,
        assessment: {
          state: cited ? "supports_consideration" : "unknown",
          need,
          cited_claims: cited ? [cited.claim.claim_id] : [],
          threshold: 20,
          unknowns: "Current availability and quality are unknown.",
        },
      }),
    ),
  );
}

it("lets a business choose metrics while the buyer selects a different relevant need", async () => {
  const fetch = vi.fn(api);
  vi.stubGlobal("fetch", fetch);
  render(<Portable />);
  const user = userEvent.setup();
  await screen.findByText("This record supports considering Juniper Kitchen.");
  await user.click(
    screen.getByRole("button", {
      name: "Average pickup preparation time",
    }),
  );
  await screen.findByText("No metrics selected.");
  expect(
    screen.queryByText("This record supports considering Juniper Kitchen."),
  ).toBeNull();
  await user.click(
    screen.getByRole("button", { name: "Average net check" }),
  );
  await screen.findByText("$26.00 per check");
  expect(
    screen.getByText(
      "There is no usable published evidence for this requirement.",
    ),
  ).toBeTruthy();
  await user.click(
    screen.getByRole("button", { name: "Understand typical check spending" }),
  );
  await screen.findByText("This record supports considering Juniper Kitchen.");
  expect(fetch.mock.calls.every(([url]) => !url.includes("cohort="))).toBe(
    true,
  );
  expect(fetch.mock.lastCall?.[0]).toContain("need=net-check");
});

it("switches business examples without carrying a claim across subjects", async () => {
  vi.stubGlobal("fetch", vi.fn(api));
  render(<Portable />);
  await screen.findAllByText("14.0 minutes");
  await userEvent
    .setup()
    .click(screen.getByRole("button", { name: "B2B services" }));
  await screen.findByText(
    "This record supports considering Northline Services.",
  );
  expect(screen.queryByText("14.0 minutes")).toBeNull();
  expect(screen.queryByText("Average pickup preparation time")).toBeNull();
});

it("withdrawal and disputes remove use despite a valid original signature", async () => {
  vi.stubGlobal("fetch", vi.fn(api));
  render(<Portable />);
  const user = userEvent.setup();
  await screen.findByText("This record supports considering Juniper Kitchen.");
  await user.click(
    screen.getByRole("button", { name: "Withdrawn" }),
  );
  await screen.findByText(/Publication withdrawn/);
  expect(
    screen.queryByText("This record supports considering Juniper Kitchen."),
  ).toBeNull();
  await user.click(
    screen.getByRole("button", { name: "Disputed" }),
  );
  await screen.findByText(/Publication disputed/);
  expect(
    screen.getByText(
      "There is no usable published evidence for this requirement.",
    ),
  ).toBeTruthy();
});

it("opens an evidence citation with provenance and returns focus after dismissal", async () => {
  vi.stubGlobal("fetch", vi.fn(api));
  render(<Portable />);
  const user = userEvent.setup();
  const citation = await screen.findByRole("button", {
    name: "fictional:restaurant:pickup",
  });
  await user.click(citation);
  const dialog = await screen.findByRole("dialog");
  expect(
    within(dialog).getByText(
      /Source accuracy and independent audit are unestablished/,
    ),
  ).toBeTruthy();
  expect(
    within(dialog).getByText("Method and signed claim").closest("details")
      ?.open,
  ).toBe(false);
  await user.keyboard("{Escape}");
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
  expect(document.activeElement).toBe(citation);
});

it("clears a successful assessment on failed reads and retries the current business", async () => {
  const fetch = vi.fn(api);
  vi.stubGlobal("fetch", fetch);
  render(<Portable />);
  const user = userEvent.setup();
  expect(screen.getByText(/Calculating and checking/)).toBeTruthy();
  await screen.findByText("This record supports considering Juniper Kitchen.");
  fetch.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "Ecommerce brand" }));
  await screen.findByRole("alert");
  expect(
    screen.queryByText("This record supports considering Juniper Kitchen."),
  ).toBeNull();
  await user.click(
    screen.getByRole("button", { name: "Retry evidence preview" }),
  );
  await screen.findByText("This record supports considering Fieldwork Goods.");
  expect(fetch.mock.lastCall?.[0]).toContain("business=ecommerce");
});
