import React from "react";
import { it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Concept } from "./Concept";

function api(url: string) {
  const scope = url.includes("context=shipped-order");
  const price = url.includes("priority=price");
  return Promise.resolve({
    ok: true,
    json: async () => ({
      state: scope ? "assessed" : "scope_not_established",
      reason: "Shipped-order evidence cannot establish pickup or meal service.",
      candidates: [
        { subject: "fictional:merchant-a", name: "Cedar Market" },
        { subject: "fictional:merchant-unknown", name: "Little Pantry" },
      ],
      decision: scope
        ? {
            choice: price
              ? "fictional:merchant-unknown"
              : "fictional:merchant-a",
          }
        : null,
    }),
  });
}

it("explains stack responsibilities and changes actual discovery inputs with consumer intent", async () => {
  const fetch = vi.fn(api);
  vi.stubGlobal("fetch", fetch);
  const compare = vi.fn();
  render(<Concept onCompare={compare} />);
  const user = userEvent.setup();
  await screen.findByRole("heading", {
    name: "Cedar Market fits this brief · $24",
  });
  await user.click(
    screen.getByRole("button", {
      name: /2. Identify the responsible business/,
    }),
  );
  expect(
    screen.getByText(/No legal-entity, branch or brand relationships/),
  ).toBeTruthy();
  await user.click(screen.getByRole("button", { name: "Lowest price" }));
  await screen.findByRole("heading", {
    name: "Little Pantry fits this brief · $18",
  });
  await user.click(screen.getByRole("button", { name: "Local pickup" }));
  await screen.findByRole("heading", {
    name: "We can’t recommend a business for this need.",
  });
  expect(screen.queryByText(/Little Pantry fits this brief/)).toBeNull();
  expect(
    fetch.mock.calls.some(
      ([url]) =>
        url.includes("context=local-pickup") && url.includes("priority=price"),
    ),
  ).toBe(true);
  await user.click(
    screen.getByRole("button", {
      name: "Explore budgets and inspect the evidence",
    }),
  );
  expect(compare).toHaveBeenCalledOnce();
});

it("removes stale business recommendations on failed reads and retries the current need", async () => {
  const fetch = vi.fn(api);
  vi.stubGlobal("fetch", fetch);
  render(<Concept onCompare={() => {}} />);
  const user = userEvent.setup();
  await screen.findByText(/Cedar Market fits this brief/);
  fetch.mockRejectedValueOnce(new Error("offline"));
  await user.click(screen.getByRole("button", { name: "Meal delivery" }));
  await screen.findByRole("alert");
  expect(screen.queryByText(/Cedar Market fits this brief/)).toBeNull();
  await user.click(
    screen.getByRole("button", { name: "Retry business assessment" }),
  );
  await screen.findByText("We can’t recommend a business for this need.");
  await waitFor(() =>
    expect(fetch.mock.lastCall?.[0]).toContain("context=prepared-meal"),
  );
});
