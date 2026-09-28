# Weighted routing — exploratory task kernel

Status: evaluator prototype in Arena 0.4.0. This is a candidate task for future
experiments, not a selected or preregistered EXP-001 benchmark. It is not yet
connected to `iterate`; that command still accepts only `integer-sum`.

## Contract

An instance contains 2–256 nodes, unique directed edges with positive integer
weights, and source/target node IDs. An answer is a simple list of node IDs from
source to target, or JSON null to claim the target is unreachable. Zero-length
routes use `[source]` when source equals target. Repeated nodes are invalid.

The evaluator reconstructs path cost from the instance. It never accepts a cost
reported by the candidate. A Dijkstra oracle calculates the exact optimum;
unit tests cross-check it against exhaustive simple-path enumeration on 50 small
generated graphs. Incorrect direction, nonexistent edges, malformed answers and
false unreachability claims are invalid.

For a valid reachable path, quality is `optimal_cost / path_cost`, with quality 1
for the zero-cost same-endpoint case. Report validity, optimality, path cost and
additive regret separately. Correct unreachability gets quality 1; invalid answers
get quality 0 and no finite additive regret. No aggregate suite score is fixed yet.
Reachability strata must be reported separately if mixed into a future suite.

## Avoid building convergence into the score

The evaluator accepts **every** optimal path. The diamond control has two distinct
optimal paths, `[0,1,3]` and `[0,2,3]`, each with quality 1 and regret 0. Thus optimal
performance does not by construction force one output sequence.

Likewise, equal output paths cannot establish common architecture or algorithm.
The reference algorithm is evaluator code, not a required candidate algorithm.
Performance, route diversity, internal structure and causal origin dependence
require separate measurements. This kernel measures only per-instance performance.

## Generation and reproducibility

`generate_case(seed=..., nodes=..., extra_edges=..., max_weight=...)` creates a
randomized directed backbone plus distinct additional edges. The backbone ensures
the chosen target is reachable; unreachable cases need a separately specified
generator or fixed control. Seed and size are adjustable. Persist the actual
`case.as_dict()` and `case.digest`, not only its seed, for a frozen experiment.
The digest ignores edge ordering but includes endpoints, weights and node IDs.

These generators and controls are public. Nothing here is claimed to be a hidden
selection suite or holdout, and no secret cases are committed. No benchmark suite
has been opened or silently added to an existing experiment.

## Remaining work before agent experiments

1. Define the candidate process interface and connect a TaskAdapter and CLI config.
2. Build distinct valid seeds and compare their baseline quality and resource use.
3. Measure whether scaling actually creates the intended resource bottlenecks;
   correctness alone may be solved trivially with the same familiar algorithm.
4. Specify development, selection, fixed anchor, regression and final-holdout
   distributions, including reachable/unreachable proportions and tie frequency.
5. Freeze aggregate scoring, runtime-noise treatment, comparison levels and
   matched-performance analysis before confirmatory runs.

Routing is useful here because answers are objectively checkable and degeneracy
can be controlled. Those properties alone do not make it a valid test of IAH.
