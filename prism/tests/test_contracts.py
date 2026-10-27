import json
import unittest
from dataclasses import replace

from prism.models import ArtifactRef, EvaluationContext, Measurement, Status
from prism.comparison import incompatibilities
from prism.reporting import render_json


class ContractTests(unittest.TestCase):
    def test_missing_measurement_is_not_zero(self):
        result = Measurement("architecture", "1", ("a:v1",), Status.NOT_MEASURED, reason="No internal access")
        record = json.loads(render_json((result,)))["measurements"][0]
        self.assertIsNone(record["value"])
        self.assertEqual(record["status"], "not_measured")
        with self.assertRaises(ValueError):
            replace(result, value=0)

    def test_measured_values_are_finite(self):
        for value in (None, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                Measurement("distance", "1", ("a:v1", "b:v1"), Status.MEASURED, value=value)

    def test_comparison_context(self):
        context = EvaluationContext("task", "a" * 64, "judge-v1", "b" * 64)
        self.assertEqual(incompatibilities(context, context), ())
        self.assertEqual(incompatibilities(context, context, resource_metric=True), ("missing:environment_id",))
        self.assertIn("different:suite_sha256", incompatibilities(context, replace(context, suite_sha256="c" * 64)))
        self.assertIn("missing:task_id", incompatibilities(context, replace(context, task_id="")))

    def test_evidence_and_stable_report(self):
        ref = ArtifactRef("results/a.json", "a" * 64)
        result = Measurement("quality", "1", ("a:v1",), Status.MEASURED, value=1, evidence=(ref,))
        self.assertEqual(render_json((result,)), render_json((result,)))
        self.assertEqual(json.loads(render_json((result,)))["measurements"][0]["evidence"][0]["sha256"], ref.sha256)
        with self.assertRaises(ValueError):
            ArtifactRef("file", "not-a-hash")
