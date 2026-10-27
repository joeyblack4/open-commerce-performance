export const hosted = import.meta.env.VITE_STATIC_DEMO === "true";
export const repository =
  "https://github.com/joeyblack4/open-commerce-performance";

export function resource(name: "brief" | "concept" | "protocol" | "schema") {
  const files = {
    brief: "proposal.pdf",
    concept: "concept.md",
    protocol: "protocol.md",
    schema: "schema.json",
  };
  const local = {
    brief: "/brief.pdf",
    concept: "/concept.md",
    protocol: "/protocol.md",
    schema: "/v0/portable-schema",
  };
  return hosted ? import.meta.env.BASE_URL + files[name] : local[name];
}

export function fixturePath(path: string) {
  const url = new URL(path, "https://example.invalid");
  const q = url.searchParams;
  const metrics: Record<string, string[]> = {
    restaurant: ["pickup", "net-check"],
    ecommerce: ["delivery", "dispatch"],
    b2b: ["response", "quote"],
  };
  if (
    url.origin !== "https://example.invalid" ||
    url.pathname !== "/v0/portable-preview" ||
    url.hash ||
    [...q.keys()].length !== 4 ||
    ["business", "claims", "state", "need"].some(
      (key) => q.getAll(key).length !== 1,
    )
  ) {
    throw new Error("Unsupported hosted preview request");
  }
  const business = q.get("business")!,
    state = q.get("state")!,
    need = q.get("need")!;
  const selected =
    q.get("claims") === "none" ? [] : q.get("claims")!.split(",");
  if (
    !Object.hasOwn(metrics, business) ||
    !["published", "withdrawn", "disputed"].includes(state) ||
    !metrics[business].includes(need) ||
    new Set(selected).size !== selected.length ||
    selected.some((id) => !metrics[business].includes(id))
  ) {
    throw new Error("Unsupported hosted preview choices");
  }
  return `fixtures/${business}--${selected.sort().join("_") || "none"}--${state}--${need}.json`;
}
