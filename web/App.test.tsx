import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "./App";
import { Shop } from "./Shop";
import { type Bundle, type Decision, type MerchantPreview } from "./types";

const metric = {
  id: "fulfilled_on_time_rate",
  status: "observed",
  value: 0.9,
  numerator: 900,
  denominator: 1000,
  coverage_fraction: 1,
  reason: "",
  followup_days: 30,
  lower_bound: null,
  upper_bound: null,
};
const evidence = {
  statement: {
    statement_id: "fixture-test-0001",
    metric,
    period: { start: "2026-04-01T00:00:00Z", end: "2026-07-01T00:00:00Z" },
    observed_at: "2026-10-25T12:00:00Z",
    expires_at: "2026-11-01T12:00:00Z",
    methodology_url: "/method",
    refund_policy: { id: "returns-accepted-60-days" },
    comparison: {
      country: "US",
      channel: "shipped",
      service: "standard",
      category: "general-commerce",
    },
  },
  verification: {
    current: true,
    signature_valid: true,
    arithmetic_consistent: true,
    calculation_reproduced: true,
    source_truth: "not_established",
  },
  envelope: { protected: "example-not-a-signature" },
};
const bundle: Bundle = {
  demo_clock: "2026-10-25T20:00:00Z",
  merchants: [
    {
      subject: "fictional:merchant-a",
      name: "Cedar Market",
      evidence: [evidence],
    },
    { subject: "fictional:merchant-b", name: "Grove Goods", evidence: [] },
    {
      subject: "fictional:merchant-unknown",
      name: "Little Pantry",
      evidence: [],
    },
  ],
};
const selected: Decision = {
  choice: "fictional:merchant-a",
  state: "selected",
  reason: "",
  assessments: [
    {
      subject: "fictional:merchant-a",
      price: 24,
      eligible: true,
      reason: "",
      historical_on_time: 0.9,
    },
    {
      subject: "fictional:merchant-b",
      price: 20,
      eligible: true,
      reason: "",
      historical_on_time: 0.75,
    },
    {
      subject: "fictional:merchant-unknown",
      price: 18,
      eligible: true,
      reason: "",
      historical_on_time: null,
    },
  ],
};
const preview: MerchantPreview = {
  preview_only: true,
  state: "shared",
  merchant: bundle.merchants[0],
  live_registry_changed: false,
  message: "",
  status_checks: [{ signature_valid: true, current: true, reason: "" }],
  categories: [],
};
const respond = (data: unknown) =>
  Promise.resolve(
    new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
function mockApi() {
  return vi.fn((url: string) => {
    if (url === "/v0/demo") return respond(bundle);
    if (url === "/v0/release-info") return respond({ prepared: true });
    if (url.startsWith("/v0/merchant-preview"))
      return respond(
        url.includes("withdrawn") || url.includes("disputed")
          ? {
              ...preview,
              merchant: { ...preview.merchant, evidence: [] },
              status_checks: [
                {
                  signature_valid: true,
                  current: false,
                  reason: "withdrawn_or_superseded",
                },
              ],
            }
          : preview,
      );
    return respond(selected);
  });
}

describe("shopper and merchant paths", () => {
  it("leads with the shopping brief and shows a budget/evidence tradeoff", async () => {
    vi.stubGlobal("fetch", mockApi());
    render(<App />);
    await screen.findByRole("heading", {
      name: "Find the delivery that fits you.",
    });
    await screen.findByText(
      "You spend $6 more than the $18 option to choose a merchant with a qualifying delivery record.",
    );
    expect(screen.getByRole("slider", { name: "Total budget" })).toBeTruthy();
    expect(screen.queryByText(/JWS signature/)).toBeNull();
  });
  it("sends real budget and threshold inputs to the bounded recommendation API", async () => {
    const fetch = mockApi();
    vi.stubGlobal("fetch", fetch);
    render(<Shop bundle={bundle} />);
    const user = userEvent.setup();
    const slider = screen.getByRole("slider", { name: "Total budget" });
    slider.focus();
    await user.keyboard("{ArrowLeft}");
    await waitFor(() =>
      expect(
        fetch.mock.calls.some(([url]) => url.includes("budget=2400")),
      ).toBe(true),
    );
    await user.click(screen.getByText("Delivery requirement: 85%+"));
    await user.click(screen.getByRole("button", { name: "75%+" }));
    await waitFor(() =>
      expect(
        fetch.mock.calls.some(([url]) => url.includes("threshold=75")),
      ).toBe(true),
    );
  });
  it("does not show a stale recommendation after changed controls fail", async () => {
    const fetch = mockApi();
    vi.stubGlobal("fetch", fetch);
    render(<Shop bundle={bundle} />);
    await screen.findByText(/You spend \$6 more/);
    fetch.mockImplementation(() => Promise.reject(new Error("offline")));
    await userEvent
      .setup()
      .click(
        within(screen.getByRole("group", { name: "Main priority" })).getByRole(
          "button",
          { name: "Lowest price" },
        ),
      );
    await screen.findByRole("alert");
    expect(screen.queryByText(/You spend \$6 more/)).toBeNull();
  });
  it("handles initial loading, error and retry", async () => {
    const fetch = vi
      .fn()
      .mockRejectedValueOnce(new Error("offline"))
      .mockImplementation(mockApi());
    vi.stubGlobal("fetch", fetch);
    render(<App />);
    expect(
      screen.getByText("Loading your fictional shopping options…"),
    ).toBeTruthy();
    await screen.findByRole("alert");
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "Try again" }));
    await screen.findByRole("heading", {
      name: "Find the delivery that fits you.",
    });
  });
  it("keeps missing evidence explicit while allowing price comparison", async () => {
    const fetch = mockApi();
    fetch.mockImplementation((url: string) =>
      url === "/v0/demo"
        ? respond({
            ...bundle,
            merchants: bundle.merchants.map((m) => ({ ...m, evidence: [] })),
          })
        : respond({
            ...selected,
            choice: null,
            state: "insufficient_evidence",
            adjustments: [
              {
                label: "Compare on price",
                budget: 25,
                priority: "price",
                threshold: 85,
                evidence: true,
                qualifier: "History unknown",
              },
            ],
          }),
    );
    vi.stubGlobal("fetch", fetch);
    render(<App />);
    await screen.findByText(
      "No usable evidence is currently shared. You can still compare prices; delivery history stays unknown.",
    );
    await screen.findByRole("heading", {
      name: "We need more evidence to choose.",
    });
    expect(
      screen.getByRole("button", { name: "Compare on price" }),
    ).toBeTruthy();
  });
  it("previews full-bundle withdrawal and restoration with no write request", async () => {
    const fetch = mockApi();
    vi.stubGlobal("fetch", fetch);
    render(<App />);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "For merchants" }));
    await screen.findByText("Delivered on time, with every item");
    await user.click(
      screen.getByRole("button", { name: "Preview withdrawal" }),
    );
    await screen.findByRole("heading", {
      name: "These claims no longer support a recommendation.",
    });
    await user.click(
      screen.getByRole("button", { name: "Sharing the full bundle" }),
    );
    await screen.findByText("Delivered on time, with every item");
    expect(
      fetch.mock.calls.every((call) => !call[0].includes("publish-real")),
    ).toBe(true);
  });
  it("shows a disputed state and source requirements instead of a connection action", async () => {
    vi.stubGlobal("fetch", mockApi());
    render(<App />);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "For merchants" }));
    await user.click(
      screen.getByRole("button", { name: "Preview a disputed record" }),
    );
    await screen.findByRole("heading", {
      name: "A disputed claim should not decide the purchase.",
    });
    expect(
      screen.queryByRole("button", { name: /Connect Shopify|Connect Square/i }),
    ).toBeNull();
  });
  it("keeps developer commands and protocol limits in the builder path", async () => {
    vi.stubGlobal("fetch", mockApi());
    render(<App />);
    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "For builders" }));
    expect(
      screen.getByRole("heading", { name: "Run it locally" }),
    ).toBeTruthy();
    expect(
      await screen.findByRole("link", { name: "Download the review package" }),
    ).toBeTruthy();
    expect(
      screen.getByText(/Unsupported clients keep the base catalog/),
    ).toBeTruthy();
  });
  it("keeps human evidence readable before the developer payload", async () => {
    vi.stubGlobal("fetch", mockApi());
    render(<Shop bundle={bundle} />);
    await userEvent
      .setup()
      .click(screen.getAllByRole("button", { name: "See the evidence" })[0]);
    await screen.findByText("900 of 1000 orders");
    expect(
      screen.getByText(/No independent source authentication/),
    ).toBeTruthy();
    const developer = screen
      .getByText("Developer statement and JWS")
      .closest("details");
    expect(developer?.open).toBe(false);
    await userEvent.setup().click(screen.getByRole("button", { name: "Done" }));
    expect(screen.queryByRole("dialog")).toBeNull();
  });
});
