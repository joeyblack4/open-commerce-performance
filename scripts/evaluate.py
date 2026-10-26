#!/usr/bin/env python3
"""Execute frozen preregistered synthetic cases; never a claim of model evaluation."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from ocp.decision import decide
from ocp.model import instant
from ocp.registry import Registry

ROOT = Path(__file__).parents[1]
plan_raw = (ROOT / "scripts/evaluation-plan.json").read_bytes()
plan = json.loads(plan_raw)
registry = Registry()
bundle = registry.bundle(instant(plan["frozen_fixture_clock"]))
results = []
for case in plan["cases"]:
    for arm in plan["arms"]:
        input_bundle = deepcopy(bundle)
        if arm in ("placebo_unusable_evidence", "tampered_evidence"):
            for merchant in input_bundle["merchants"]:
                for evidence in merchant["evidence"]:
                    evidence["verification"]["current"] = False
                    evidence["verification"]["signature_valid"] = False
        decision = decide(input_bundle, case["scenario"], arm != "base_without_evidence")
        choice = decision["choice"]
        selected = next((a for a in decision["assessments"] if a["subject"] == choice), None)
        results.append(
            {
                "scenario": case["scenario"],
                "arm": arm,
                "choice": choice,
                "hard_constraints_satisfied": selected["eligible"] if selected else None,
                "expectation_agreement": choice == case["expected_choice"],
                "abstained": choice is None,
            }
        )
report = {
    "plan_sha256": sha256(plan_raw).hexdigest(),
    "kind": plan["type"],
    "results": results,
    "decision_regret": None,
    "consumer_or_model_validation": False,
    "limitations": plan["limitations"],
}
print(json.dumps(report, indent=2))
if any(x["hard_constraints_satisfied"] is False for x in results):
    raise SystemExit(1)
