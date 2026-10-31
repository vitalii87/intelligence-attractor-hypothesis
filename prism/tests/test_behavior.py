import json
import unittest
from dataclasses import replace

from prism.metrics.behavior import (BehaviorSample, CaseKey, Observation,
                                    compare_behavior, render_behavior)
from prism.models import EntityVersion, EvaluationContext, Status


class BehaviorTests(unittest.TestCase):
    def setUp(self):
        self.keys = (CaseKey("a", "1"), CaseKey("b", "1"), CaseKey("a", "2"))
        context = EvaluationContext("task", "a" * 64, "v1", "b" * 64)
        self.left = BehaviorSample(EntityVersion("left", "v1"), context,
                                   tuple(Observation(k, "yes") for k in self.keys))
        self.right = replace(self.left, entity=EntityVersion("right", "v1"))

    def test_known_equal_partial_and_divergent_outputs(self):
        for count in (0, 1, 3):
            right = replace(self.right, observations=tuple(
                Observation(k, "no" if i < count else "yes") for i, k in enumerate(self.keys)))
            result = compare_behavior(self.left, right, self.keys)
            self.assertEqual(result.measurement.value, count / 3)
            self.assertEqual(len(result.disagreements), count)
            self.assertEqual(compare_behavior(right, self.left, self.keys).measurement.value, count / 3)

    def test_missing_and_failed_never_become_agreement(self):
        right = replace(self.right, observations=(Observation(self.keys[0], "yes"),
                                                  Observation(self.keys[1], None, "timeout")))
        result = compare_behavior(self.left, right, self.keys)
        self.assertEqual(result.measurement.status, Status.NOT_MEASURED)
        self.assertIsNone(result.measurement.value)
        self.assertEqual(result.missing_right, (self.keys[2],))
        self.assertEqual(result.failed_right, (self.keys[1],))
        self.assertEqual(result.paired, (self.keys[0],))
        empty = replace(self.right, observations=())
        self.assertIsNone(compare_behavior(empty, empty, self.keys).measurement.value)

    def test_incompatible_conditions_prevent_pairing(self):
        for field in ("task_id", "suite_sha256", "evaluator_version", "protocol_sha256"):
            right = replace(self.right, context=replace(self.right.context, **{field: "other"}))
            result = compare_behavior(self.left, right, self.keys)
            self.assertEqual(result.measurement.status, Status.INCOMPATIBLE)
            self.assertEqual(result.paired, ())

    def test_ambiguous_or_unexpected_alignment_rejected(self):
        for keys in ((), self.keys + (self.keys[0],)):
            with self.assertRaises(ValueError):
                compare_behavior(self.left, self.right, keys)
        for observations in (self.right.observations * 2,
                             (Observation(CaseKey("unknown", "1"), "yes"),)):
            with self.assertRaises(ValueError):
                compare_behavior(self.left, replace(self.right, observations=observations), self.keys)

    def test_order_invariance_and_report_context(self):
        normal = render_behavior(compare_behavior(self.left, self.right, self.keys))
        reordered = replace(self.right, observations=self.right.observations[::-1])
        self.assertEqual(normal, render_behavior(compare_behavior(self.left, reordered, self.keys[::-1])))
        report = json.loads(normal)
        self.assertEqual(report["coverage"], {"expected": 3, "paired": 3})
        self.assertEqual(report["right"]["context"]["task_id"], "task")

    def test_exact_strings_and_empty_output(self):
        key = (self.keys[0],)
        left = replace(self.left, observations=(Observation(key[0], ""),))
        right = replace(self.right, observations=(Observation(key[0], " "),))
        self.assertEqual(compare_behavior(left, right, key).measurement.value, 1)
        for output, failure in ((None, None), ("output", "timeout"), (None, "")):
            with self.assertRaises(ValueError):
                Observation(key[0], output, failure)
