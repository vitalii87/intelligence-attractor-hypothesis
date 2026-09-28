"""Exploratory positive-weight directed routing kernel, not EXP-001 registration."""
from dataclasses import dataclass
import hashlib
import heapq
import json
import random


@dataclass(frozen=True)
class RoutingCase:
    nodes: int
    edges: tuple[tuple[int, int, int], ...]
    source: int
    target: int

    def __post_init__(self):
        if type(self.nodes) is not int or not 2 <= self.nodes <= 256:
            raise ValueError("nodes must be an integer in [2, 256]")
        if any(type(v) is not int or not 0 <= v < self.nodes for v in (self.source, self.target)):
            raise ValueError("invalid endpoint")
        if not isinstance(self.edges, tuple):
            raise ValueError("edges must be immutable tuples")
        seen = set()
        for edge in self.edges:
            if not isinstance(edge, tuple) or len(edge) != 3:
                raise ValueError("edge must be a triple")
            u, v, weight = edge
            if any(type(x) is not int for x in edge) or not 0 <= u < self.nodes or not 0 <= v < self.nodes or u == v or not 1 <= weight <= 10000:
                raise ValueError("invalid directed positive-weight edge")
            if (u, v) in seen:
                raise ValueError("duplicate edge")
            seen.add((u, v))

    def as_dict(self):
        return {"nodes": self.nodes, "edges": [list(e) for e in sorted(self.edges)],
                "source": self.source, "target": self.target}

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def optimal_cost(case: RoutingCase) -> int | None:
    """Independent evaluator oracle; candidate paths never supply their own cost."""
    graph = [[] for _ in range(case.nodes)]
    for u, v, weight in case.edges:
        graph[u].append((v, weight))
    distances = {case.source: 0}
    queue = [(0, case.source)]
    while queue:
        cost, node = heapq.heappop(queue)
        if cost != distances[node]:
            continue
        if node == case.target:
            return cost
        for neighbor, weight in graph[node]:
            candidate = cost + weight
            if neighbor not in distances or candidate < distances[neighbor]:
                distances[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))
    return None


def score_path(case: RoutingCase, answer) -> dict:
    """Answer is a simple node list, or null to claim unreachability."""
    optimum = optimal_cost(case)
    result = {"valid": False, "optimal": False, "quality": 0.0,
              "path_cost": None, "optimal_cost": optimum, "additive_regret": None}
    if answer is None:
        if optimum is None:
            result.update(valid=True, optimal=True, quality=1.0, reason="correctly_unreachable")
        else:
            result["reason"] = "false_unreachable"
        return result
    if not isinstance(answer, list) or not 1 <= len(answer) <= case.nodes or any(type(v) is not int or not 0 <= v < case.nodes for v in answer):
        return {**result, "reason": "invalid_path_format"}
    if answer[0] != case.source or answer[-1] != case.target or len(set(answer)) != len(answer):
        return {**result, "reason": "invalid_endpoints_or_cycle"}
    weights = {(u, v): w for u, v, w in case.edges}
    if any((u, v) not in weights for u, v in zip(answer, answer[1:])):
        return {**result, "reason": "nonexistent_directed_edge"}
    cost = sum(weights[u, v] for u, v in zip(answer, answer[1:]))
    assert optimum is not None
    return {**result, "valid": True, "optimal": cost == optimum,
            "quality": 1.0 if cost == 0 else optimum / cost,
            "path_cost": cost, "additive_regret": cost - optimum, "reason": "valid_path"}


def generate_case(*, seed: int, nodes: int, extra_edges: int, max_weight: int = 20) -> RoutingCase:
    """Connected directed backbone plus sampled edges. Freeze generated cases, not just seeds."""
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    if type(nodes) is not int or not 2 <= nodes <= 256:
        raise ValueError("nodes must be in [2, 256]")
    if type(extra_edges) is not int or not 0 <= extra_edges <= (nodes - 1) ** 2:
        raise ValueError("extra_edges exceeds directed graph capacity")
    if type(max_weight) is not int or not 1 <= max_weight <= 10000:
        raise ValueError("invalid maximum weight")
    rng = random.Random(seed)
    order = list(range(nodes))
    rng.shuffle(order)
    edges = {(u, v): rng.randint(1, max_weight) for u, v in zip(order, order[1:])}
    available = [(u, v) for u in range(nodes) for v in range(nodes) if u != v and (u, v) not in edges]
    for u, v in rng.sample(available, extra_edges):
        edges[u, v] = rng.randint(1, max_weight)
    return RoutingCase(nodes, tuple((u, v, w) for (u, v), w in sorted(edges.items())), order[0], order[-1])


# Deliberate degeneracy control: both [0,1,3] and [0,2,3] are optimal.
DIAMOND = RoutingCase(4, ((0, 1, 1), (1, 3, 1), (0, 2, 1), (2, 3, 1)), 0, 3)
