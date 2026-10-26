import copy
from dataclasses import replace
import unittest
from jsonschema.exceptions import ValidationError
from ocp.adapters.shopify_mock import read_snapshot, without_delivery
from ocp.contract import encode, parse_json, parse_statement, validate
from ocp.metrics import calculate, compare
from ocp.model import instant
from ocp.statements import make_statement, reproduce


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, _ = read_snapshot("fixture-a")
        cls.b, _ = read_snapshot("fixture-b")
        cls.unknown, _ = read_snapshot("fixture-unknown")

    def test_exact_reference_counts(self):
        for snap, counts in [(self.a, [900, 950, 50]), (self.b, [750, 800, 150])]:
            for metric, n in zip(
                ["fulfilled_on_time_rate", "order_complete_rate", "order_refund_incidence"],
                counts,
                strict=True,
            ):
                m = calculate(snap, metric)
                self.assertEqual((m["numerator"], m["denominator"], m["value"]), (n, 1000, n / 1000))
                self.assertEqual(m["coverage_fraction"], 1)

    def test_pure_repeatable_and_order_independent(self):
        before = copy.deepcopy(self.a)
        for metric in ["fulfilled_on_time_rate", "order_complete_rate", "order_refund_incidence"]:
            self.assertEqual(
                calculate(self.a, metric), calculate(replace(self.a, orders=self.a.orders[::-1]), metric)
            )
        self.assertEqual(before, self.a)

    def test_unknown_not_zero(self):
        for metric in ["fulfilled_on_time_rate", "order_complete_rate", "order_refund_incidence"]:
            m = make_statement(self.unknown, metric)["metric"]
            self.assertEqual(m["status"], "not_observed")
            self.assertIsNone(m["value"])
            self.assertIsNone(m["numerator"])
            self.assertIsNone(m["denominator"])

    def test_fulfillment_does_not_prove_delivery(self):
        self.assertIsNone(calculate(without_delivery(self.a), "fulfilled_on_time_rate")["value"])
        fake = replace(
            self.a, orders=tuple(replace(o, delivery_evidence="merchant_assertion") for o in self.a.orders)
        )
        self.assertIsNone(calculate(fake, "fulfilled_on_time_rate")["value"])

    def test_partial_bounds_and_coverage(self):
        s = replace(
            self.a,
            orders=tuple(
                replace(o, delivered_at=None) if i >= 900 else o for i, o in enumerate(self.a.orders)
            ),
        )
        m = make_statement(s, "fulfilled_on_time_rate")["metric"]
        self.assertEqual(m["status"], "partial")
        self.assertEqual((m["lower_bound"], m["upper_bound"], m["coverage_fraction"]), (0.8, 0.9, 0.9))
        self.assertIsNone(m["value"])

    def test_incomplete_source_no_invented_denominator(self):
        s = replace(self.a, expected_orders=1200, complete=False)
        m = make_statement(s, "fulfilled_on_time_rate")["metric"]
        self.assertEqual(m["status"], "partial")
        for key in ["value", "eligible_n", "denominator", "coverage_fraction", "lower_bound", "upper_bound"]:
            self.assertIsNone(m[key])

    def test_missing_entire_rows_complete_flag_rejected(self):
        with self.assertRaises(ValueError):
            calculate(replace(self.a, expected_orders=1200), "order_refund_incidence")

    def test_cancelled_orders_not_deleted(self):
        s = replace(
            self.a,
            orders=tuple(replace(o, cancelled=True) if i < 100 else o for i, o in enumerate(self.a.orders)),
        )
        m = make_statement(s, "order_refund_incidence")["metric"]
        self.assertEqual((m["denominator"], m["cancelled_n"]), (1000, 100))

    def test_sparse_diagnostics_suppress_whole_statement(self):
        for alteration in [
            dict(cancelled=True),
            dict(fulfilled_at=None),
            dict(delivered_at=None),
            dict(paid=False),
            dict(test=True),
        ]:
            orders = (replace(self.a.orders[0], **alteration),) + self.a.orders[1:]
            statement = make_statement(replace(self.a, orders=orders), "fulfilled_on_time_rate")
            self.assertEqual(statement["metric"]["status"], "suppressed", alteration)
            for field in [
                "value",
                "cohort_n",
                "eligible_n",
                "observed_n",
                "unknown_n",
                "censored_n",
                "cancelled_n",
                "unfulfilled_n",
            ]:
                self.assertIsNone(statement["metric"][field])
            self.assertIsNone(statement["lineage"]["source_record_count"])
        s = make_statement(replace(self.a, expected_orders=1001, complete=False), "order_complete_rate")
        self.assertEqual(s["metric"]["status"], "suppressed")

    def test_small_cohort_and_sparse_outcome(self):
        for orders in [self.a.orders[:5], self.a.orders[99:]]:
            s = replace(self.a, orders=orders, expected_orders=len(orders))
            m = make_statement(s, "fulfilled_on_time_rate")["metric"]
            self.assertEqual(m["status"], "suppressed")
            self.assertIsNone(m["value"])

    def test_no_arbitrary_slicing(self):
        with self.assertRaises(ValueError):
            calculate(replace(self.a, start="2026-04-02T00:00:00Z"), "order_complete_rate")

    def test_maturity_and_refund_boundary(self):
        immature = replace(
            self.a,
            observed_at="2026-07-01T00:00:00Z",
            orders=tuple(
                replace(
                    o,
                    purchased_at="2026-06-01T12:00:00Z",
                    fulfilled_at=None,
                    delivered_at=None,
                    refunds_settled_at=(),
                )
                for o in self.a.orders
            ),
        )
        m = make_statement(immature, "order_refund_incidence")["metric"]
        self.assertEqual(m["status"], "suppressed")
        # Day 60 exactly excluded; duplicated partial refunds count once per order.
        orders = tuple(replace(o, refunds_settled_at=("2026-06-14T12:00:00Z",)) for o in self.a.orders)
        self.assertEqual(calculate(replace(self.a, orders=orders), "order_refund_incidence")["value"], 0)
        orders = tuple(
            replace(o, refunds_settled_at=("2026-05-01T00:00:00Z",) * 2) if i < 50 else o
            for i, o in enumerate(self.a.orders)
        )
        self.assertEqual(calculate(replace(self.a, orders=orders), "order_refund_incidence")["numerator"], 50)

    def test_exact_line_items_no_substitution(self):
        s = replace(
            self.a,
            orders=tuple(
                replace(o, fulfilled=(("fixture-sku-substitute", 2),)) if i < 100 else o
                for i, o in enumerate(self.a.orders)
            ),
        )
        self.assertEqual(calculate(s, "order_complete_rate")["numerator"], 900)

    def test_repromising_disputed(self):
        s = replace(
            self.a,
            orders=(replace(self.a.orders[0], promise_recorded_at="2026-04-16T12:00:00Z"),)
            + self.a.orders[1:],
        )
        m = make_statement(s, "fulfilled_on_time_rate")["metric"]
        self.assertEqual(m["status"], "disputed")
        self.assertIsNone(m["value"])

    def test_tenant_duplicate_and_future_events_rejected(self):
        for orders in [
            (replace(self.a.orders[0], tenant="fixture-b"),) + self.a.orders[1:],
            (self.a.orders[0],) + self.a.orders,
            (replace(self.a.orders[0], delivered_at="2027-01-01T00:00:00Z"),) + self.a.orders[1:],
        ]:
            with self.assertRaises(ValueError):
                calculate(replace(self.a, orders=orders, expected_orders=len(orders)), "order_complete_rate")

    def test_bounded_inputs_and_no_empty_commitment_success(self):
        for value in [-1, True, 1000001]:
            with self.assertRaises(ValueError):
                calculate(
                    replace(
                        self.a,
                        orders=(replace(self.a.orders[0], committed=(("fixture-sku-1", value),)),)
                        + self.a.orders[1:],
                    ),
                    "order_complete_rate",
                )
        with self.assertRaises(ValueError):
            calculate(
                replace(self.a, orders=(replace(self.a.orders[0], committed=()),) + self.a.orders[1:]),
                "order_complete_rate",
            )

    def test_subject_comparison_and_refund_policy(self):
        a = make_statement(self.a, "order_refund_incidence")
        b = make_statement(self.b, "order_refund_incidence")
        self.assertTrue(compare(a, b)["comparable"])
        b["refund_policy"]["id"] = "no-refunds"
        self.assertFalse(compare(a, b)["comparable"])
        for metric in ["repeat_purchase_rate", "product_failure_rate"]:
            with self.assertRaises(ValueError):
                calculate(self.a, metric)

    def test_aggregate_schema_and_reproduction(self):
        s = make_statement(self.a, "fulfilled_on_time_rate")
        self.assertEqual(parse_statement(encode(s)), s)
        self.assertTrue(reproduce(s, self.a))
        s["metric"]["value"] = 0.75
        s["metric"]["numerator"] = 750
        self.assertFalse(reproduce(s, self.a))
        self.assertFalse(reproduce(s, self.b))

    def test_population_contradictions_rejected(self):
        changes = [
            ("lineage", "source_record_count", 1),
            ("lineage", "expected_record_count", 999),
            ("metric", "cancelled_n", 1000000),
            ("metric", "unfulfilled_n", 100),
            ("metric", "eligible_n", 999),
            ("metric", "observed_n", 999),
            ("metric", "unknown_n", 5),
            ("metric", "coverage_fraction", 0.999),
            ("metric", "cohort_n", 1001),
        ]
        for group, key, value in changes:
            s = make_statement(self.a, "order_complete_rate")
            s[group][key] = value
            with self.assertRaises((ValueError, ValidationError), msg=key):
                validate(s)

    def test_schema_rejects_pii_extra_fields_assurance_and_product_binding(self):
        for group, key, value in [
            ("subject", "email", "customer@example.com"),
            ("assurance", "independently_audited", True),
            ("subject", "type", "product_model"),
            ("issuer", "id", "https://attacker.invalid"),
            ("metric", "value", 0),
            ("metric", "denominator", 0),
        ]:
            s = make_statement(self.a, "order_complete_rate")
            s[group][key] = value
            with self.assertRaises((ValueError, ValidationError)):
                validate(s)
        s = make_statement(self.a, "order_complete_rate")
        s["notes"] = "raw customer order synthetic-0000"
        with self.assertRaises(ValidationError):
            validate(s)

    def test_strict_json_parser(self):
        for raw in [
            b'{"x":1,"x":2}',
            b'{"x":NaN}',
            b'{"x":1e999}',
            b"[" * 50 + b"]" * 50,
            b" " * 65000,
            b"\xff",
        ]:
            with self.assertRaises(ValueError):
                parse_json(raw)

    def test_all_public_projection_has_no_order_customer_identifiers(self):
        for snapshot in [self.a, self.b, self.unknown]:
            for metric in ["fulfilled_on_time_rate", "order_complete_rate", "order_refund_incidence"]:
                raw = encode(make_statement(snapshot, metric)).decode()
                for private in [
                    "synthetic-0000",
                    "fixture-sku-",
                    "order_id",
                    "email",
                    "customer_id",
                    "token",
                ]:
                    self.assertNotIn(private, raw)

    def test_utc_required(self):
        for t in ["2026-10-25T12:00:00", "2026-10-25T12:00:00-07:00"]:
            with self.assertRaises(ValueError):
                instant(t)
