import unittest
from dataclasses import replace

from iah_arena.tasks.routing import DIAMOND, RoutingCase, generate_case, optimal_cost, score_path


def exhaustive_cost(case):
    # Independent small-graph check: enumerate simple paths without Dijkstra.
    def visit(node, visited, cost):
        if node == case.target:
            yield cost
        else:
            for u, v, w in case.edges:
                if u == node and v not in visited:
                    yield from visit(v, visited | {v}, cost + w)
    return min(visit(case.source, {case.source}, 0), default=None)


class RoutingTests(unittest.TestCase):
    def test_oracle_matches_exhaustive_small_graphs(self):
        for seed in range(50):
            case = generate_case(seed=seed, nodes=6, extra_edges=seed % 12)
            self.assertEqual(optimal_cost(case), exhaustive_cost(case))

    def test_equal_optima_not_penalized(self):
        for path in ([0, 1, 3], [0, 2, 3]):
            self.assertEqual(score_path(DIAMOND, path)["quality"], 1)
            self.assertEqual(score_path(DIAMOND, path)["additive_regret"], 0)

    def test_valid_suboptimal_and_invalid_claims(self):
        case = RoutingCase(3, ((0, 1, 1), (1, 2, 1), (0, 2, 4)), 0, 2)
        scored = score_path(case, [0, 2])
        self.assertTrue(scored["valid"])
        self.assertFalse(scored["optimal"])
        self.assertEqual(scored["quality"], 0.5)
        self.assertEqual(scored["additive_regret"], 2)
        for bad in (None, [], [False, 2], [0, 0, 2], [0, 3, 2], {"cost": 0}, [2, 0], [0, 1.0, 2]):
            self.assertFalse(score_path(case, bad)["valid"])

    def test_unreachable_direction_and_same_endpoint(self):
        case = RoutingCase(2, ((1, 0, 1),), 0, 1)
        self.assertIsNone(optimal_cost(case))
        self.assertTrue(score_path(case, None)["optimal"])
        self.assertFalse(score_path(case, [0, 1])["valid"])
        same = replace(case, target=0)
        self.assertEqual(score_path(same, [0])["quality"], 1)
        self.assertFalse(score_path(same, None)["valid"])

    def test_reproducibility_and_digest(self):
        a = generate_case(seed=42, nodes=10, extra_edges=20)
        self.assertEqual(a, generate_case(seed=42, nodes=10, extra_edges=20))
        self.assertEqual(a.digest, replace(a, edges=tuple(reversed(a.edges))).digest)
        self.assertNotEqual(a.digest, generate_case(seed=43, nodes=10, extra_edges=20).digest)
        self.assertIsNotNone(optimal_cost(a))

    def test_invalid_inputs(self):
        for edges in (((0, 1, 0),), ((0, 1, -1),), ((0, 1, 1), (0, 1, 2)), ((0, 0, 1),)):
            with self.assertRaises(ValueError):
                RoutingCase(2, edges, 0, 1)
        with self.assertRaises(ValueError):
            generate_case(seed=1, nodes=2, extra_edges=2)
