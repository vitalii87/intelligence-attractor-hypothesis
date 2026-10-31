# Exact behavioral disagreement (0.3.0)

Python API: `prism.metrics.behavior`. This first measurement compares strings on
an explicit, nonempty universe of `(case_id, replicate_id)` keys. It does not
infer case alignment from observation order. Replicate IDs must denote matched
evaluation repetitions under the caller's protocol, not independent lineages.

```python
from prism.models import EntityVersion, EvaluationContext
from prism.metrics.behavior import (
    BehaviorSample, CaseKey, Observation, compare_behavior, render_behavior,
)

context = EvaluationContext("routing", "a" * 64, "evaluator-v1", "b" * 64)
keys = (CaseKey("diamond", "1"),)
left = BehaviorSample(EntityVersion("agent-a", "v1"), context,
                      (Observation(keys[0], "s->a->t"),))
right = BehaviorSample(EntityVersion("agent-b", "v1"), context,
                       (Observation(keys[0], "s->b->t"),))
print(render_behavior(compare_behavior(left, right, keys)))
```

The example hashes are placeholders. Actual callers must supply real suite and
protocol identities. Both routes may be equally optimal: a disagreement value
of 1 says only that their output strings differ, not that either route is worse.

## Contract and interpretation

- Metric `behavior.exact-output-disagreement`, version `1`, unit `fraction`:
  differing outputs divided by declared keys, with equal weight per key.
- No whitespace, Unicode, JSON or semantic normalization. Empty strings are valid
  outputs; `None` requires a nonempty failure reason.
- Missing or failed observations produce `not_measured` with no numeric score.
  Partial successfully paired keys and disagreements remain visible diagnostics.
- Different or missing task/suite/evaluator/protocol identities produce
  `incompatible`; outputs are not paired across those contexts.
- Duplicate, unexpected or empty expected-key universes are rejected.
- JSON retains contexts, version identities, observations, failures, coverage,
  evidence references and metric settings. Reports contain raw outputs; review
  disclosure before sharing. Reference hashes are not verified by this API.

Declare the expected keys before inspecting results. Changing the universe or
replicate counts changes weighting. Matching context fields is necessary but does
not establish scientific comparability. There is no uncertainty estimate, causal
inference, quality score or architectural measurement here.

Automatic ingestion of Arena evaluation observations, binding those observations
to verified artifacts, and a comparison CLI remain planned. The ArtifactStore
importer currently imports version snapshots, not complete behavioral runs.
