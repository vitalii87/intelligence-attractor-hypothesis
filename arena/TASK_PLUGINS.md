# Task and curriculum plug-ins

The arena core does not define the experimental world. A task plug-in supplies a parameterized task family while conforming to frozen arena-owned contracts.

The first example is [`tasks/integer_sum.py`](src/iah_arena/tasks/integer_sum.py).
It measures exact arithmetic correctness through an injected runtime, while
`PolicyEvaluator` controls acceptance. Its seeds and improvements are scripted.
Only development and selection suites are exercised; the other suite identities
are reserved. This is not the frozen EXP-001 task. See the [demo guide](TASK_DEMO.md)
for commands, requirements, expected results and limitations.

## Required identity

Every plug-in declares:

- task ID and version;
- evaluator version;
- an ordered curriculum specification;
- development, selection, anchor, regression, and final-holdout suite identities;
- a stage-specific objective, public-test runner, and evaluator factory.

The curriculum is hashed from its complete canonical specification. Stage IDs, parameters, thresholds, suite versions, and confirmatory/exploratory labels therefore cannot change silently between lineages.

## Curriculum behavior

Stages have contiguous ordinals and fixed promotion rules. A promotion rule identifies one metric, its direction, threshold, and minimum number of evaluations. The scheduler records one of three outcomes:

- remain at the current stage;
- promote, or complete the final stage;
- attrit when the declared budget is exhausted.

Lineages may reach stages at different times. Analysis must match them by stage, performance, and budget rather than raw iteration number.

The API supports structural curriculum changes, but marking a stage `confirmatory` does not make it scientifically confirmatory. Any structural pressure intended for confirmatory analysis still needs preregistration before outcome inspection.

## Benchmark separation

All five suite kinds are mandatory:

- development: detailed optimizer-visible feedback;
- selection: aggregate acceptance metrics, cases hidden;
- anchor: fixed longitudinal comparisons across stages;
- regression: earlier capabilities and forgetting;
- final holdout: queried only after optimization closes.

The current types freeze their identities. Final-holdout opening is enforced by the experiment-run state machine rather than candidate code; the trusted suite launcher must use that gate.

## Fitness and acceptance

Every metric declares its direction, tolerance, optional feasibility bounds, and optional scalar weight. The arena can apply either:

- strict Pareto improvement;
- a preregistered weighted score with a minimum improvement.

The `PolicyEvaluator` discards any acceptance flag returned by task code and derives the decision from the candidate vector, incumbent vector, and frozen arena policy. Component metrics and Pareto relation remain in telemetry even under scalar selection.

The separate Pareto archive retains trade-off and numerically equivalent solutions instead of collapsing them into one winner. This is necessary for detecting persistent degeneracy.

## Artifact provenance

Accepted candidates can be captured in a content-and-provenance-addressed store. Each manifest includes file hashes plus lineage, generation, parent, task/evaluator/curriculum versions, environment digest, arena commit, seed, optimizer identity, and additional frozen metadata. A changed byte or changed provenance field produces a different artifact ID.
