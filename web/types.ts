export type Metric = {
  id: string;
  status: string;
  value: number | null;
  numerator: number | null;
  denominator: number | null;
  coverage_fraction: number | null;
  reason: string;
  followup_days: number;
  lower_bound: number | null;
  upper_bound: number | null;
};
export type Statement = {
  statement_id: string;
  metric: Metric;
  period: { start: string; end: string };
  observed_at: string;
  expires_at: string;
  methodology_url: string;
  refund_policy: { id: string };
  comparison: {
    country: string;
    channel: string;
    service: string;
    category: string;
  };
};
export type Evidence = {
  statement: Statement;
  verification: {
    signature_valid: boolean;
    current: boolean;
    calculation_reproduced: boolean;
    arithmetic_consistent: boolean;
    source_truth: string;
  };
  envelope: unknown;
};
export type Merchant = { subject: string; name: string; evidence: Evidence[] };
export type Bundle = { merchants: Merchant[]; demo_clock: string };
export type Preferences = {
  budget: number;
  priority: "price" | "delivery";
  threshold: number;
  evidence: boolean;
};
export type Assessment = {
  subject: string;
  price: number;
  eligible: boolean;
  reason: string;
  historical_on_time: number | null;
};
export type Decision = {
  choice: string | null;
  state: string;
  reason: string;
  limitations?: string;
  adjustments?: (Preferences & { label: string; qualifier: string })[];
  assessments: Assessment[];
};
export type MerchantPreview = {
  preview_only: boolean;
  state: string;
  merchant: Merchant;
  live_registry_changed: boolean;
  message: string;
  status_checks: {
    signature_valid: boolean;
    current: boolean;
    reason: string;
  }[];
  categories: { id: string; publication: string; scope: string }[];
};
export const labels: Record<string, string> = {
  fulfilled_on_time_rate: "Delivered on time, with every item",
  order_complete_rate: "Complete when marked fulfilled",
  order_refund_incidence: "Orders with a settled refund",
};
export const offers: Record<string, number> = {
  "fictional:merchant-a": 24,
  "fictional:merchant-b": 20,
  "fictional:merchant-unknown": 18,
};
export const periodLabel = "Apr–Jun 2026";
export function rate(metric?: Metric) {
  return metric?.value === null || metric?.value === undefined
    ? "Unknown"
    : `${Math.round(metric.value * 100)}%`;
}
export function date(value: string) {
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}
