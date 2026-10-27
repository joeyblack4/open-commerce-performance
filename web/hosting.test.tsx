import { expect, it } from "vitest";
import { fixturePath } from "./hosting";

it("maps publication choices to the same finite static files regardless of metric order", () => {
  const query =
    "/v0/portable-preview?business=restaurant&claims=pickup,net-check&state=published&need=pickup";
  expect(fixturePath(query)).toBe(
    "fixtures/restaurant--net-check_pickup--published--pickup.json",
  );
  expect(fixturePath(query.replace("pickup,net-check", "none"))).toContain(
    "--none--published--",
  );
});

it("does not turn arbitrary inputs or source filters into hosted file reads", () => {
  const query =
    "/v0/portable-preview?business=restaurant&claims=pickup&state=published&need=pickup";
  for (const path of [
    query + "&cohort=favorable",
    query + "&claims=pickup",
    query.replace("restaurant", "__proto__"),
    query.replace("claims=pickup", "claims=../../private"),
    query.replace("claims=pickup", "claims=pickup,pickup"),
    query.replace("need=pickup", "need=response"),
    "https://evil.example/v0/portable-preview?" + query.split("?")[1],
  ]) {
    expect(() => fixturePath(path)).toThrow();
  }
});
