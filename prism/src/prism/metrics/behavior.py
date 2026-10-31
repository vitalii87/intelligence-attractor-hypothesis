"""Exact output disagreement on an explicitly declared case/replicate universe."""
from dataclasses import asdict, dataclass
import json

from .. import __version__
from ..comparison import incompatibilities
from ..models import ArtifactRef, EntityVersion, EvaluationContext, Measurement, Status


@dataclass(frozen=True, order=True)
class CaseKey:
    case_id: str
    replicate_id: str

    def __post_init__(self):
        if not self.case_id or not self.replicate_id:
            raise ValueError("case and replicate IDs are required")


@dataclass(frozen=True)
class Observation:
    key: CaseKey
    output: str | None
    failure: str | None = None

    def __post_init__(self):
        if self.failure is None:
            if not isinstance(self.output, str):
                raise ValueError("successful observations require a string output")
        elif not isinstance(self.failure, str) or not self.failure or self.output is not None:
            raise ValueError("failed observations require a reason and no output")


@dataclass(frozen=True)
class BehaviorSample:
    entity: EntityVersion
    context: EvaluationContext
    observations: tuple[Observation, ...]
    evidence: tuple[ArtifactRef, ...] = ()


@dataclass(frozen=True)
class BehaviorComparison:
    left: BehaviorSample
    right: BehaviorSample
    expected: tuple[CaseKey, ...]
    measurement: Measurement
    paired: tuple[CaseKey, ...]
    disagreements: tuple[CaseKey, ...]
    missing_left: tuple[CaseKey, ...]
    missing_right: tuple[CaseKey, ...]
    failed_left: tuple[CaseKey, ...]
    failed_right: tuple[CaseKey, ...]


def compare_behavior(left: BehaviorSample, right: BehaviorSample,
                     expected: tuple[CaseKey, ...]) -> BehaviorComparison:
    """Strict complete coverage; partial pairs are diagnostics, never a score.

    Each declared case/replicate has equal weight. Strings are compared verbatim:
    no trimming, JSON normalization, semantic or task-quality interpretation.
    """
    universe = set(expected)
    if not universe or len(universe) != len(expected):
        raise ValueError("expected keys must be nonempty and unique")

    def index(sample):
        result = {}
        for item in sample.observations:
            if item.key in result:
                raise ValueError("duplicate case/replicate observation")
            if item.key not in universe:
                raise ValueError("observation outside declared case/replicate universe")
            result[item.key] = item
        return result

    a, b = index(left), index(right)
    missing_a, missing_b = universe - a.keys(), universe - b.keys()
    failed_a = {key for key, item in a.items() if item.failure is not None}
    failed_b = {key for key, item in b.items() if item.failure is not None}
    reasons = incompatibilities(left.context, right.context)
    paired = set() if reasons else universe - missing_a - missing_b - failed_a - failed_b
    different = {key for key in paired if a[key].output != b[key].output}
    status, reason, value = Status.MEASURED, None, None
    if reasons:
        status, reason = Status.INCOMPATIBLE, "; ".join(reasons)
    elif len(paired) != len(universe):
        status, reason = Status.NOT_MEASURED, "Incomplete successful coverage; inspect missing and failed keys."
    else:
        value = len(different) / len(universe)
    # JSON tuples avoid collisions between entity IDs and version IDs containing ':'.
    subjects = tuple(json.dumps([s.entity.entity_id, s.entity.version_id],
                               ensure_ascii=False) for s in (left, right))
    evidence = tuple(sorted(set(left.evidence + right.evidence),
                            key=lambda ref: (ref.location, ref.sha256)))
    measurement = Measurement("behavior.exact-output-disagreement", "1", subjects,
                              status, value=value, unit="fraction", reason=reason,
                              evidence=evidence)
    ordered = lambda keys: tuple(sorted(keys))
    return BehaviorComparison(left, right, ordered(universe), measurement,
                              ordered(paired), ordered(different), ordered(missing_a),
                              ordered(missing_b), ordered(failed_a), ordered(failed_b))


def render_behavior(result: BehaviorComparison) -> str:
    """Self-contained report; includes raw outputs, so callers control disclosure."""
    body = asdict(result)
    for side in ("left", "right"):
        body[side]["observations"] = sorted(body[side]["observations"],
            key=lambda item: (item["key"]["case_id"], item["key"]["replicate_id"]))
    body.update(schema_version="prism-behavior-v1", prism_version=__version__,
                coverage={"expected": len(result.expected), "paired": len(result.paired)},
                parameters={"alignment": "case_id+replicate_id", "weighting": "equal-per-key",
                            "output_equivalence": "exact-string", "coverage_policy": "complete"},
                limitations=["Output disagreement is not quality or architectural distance.",
                             "Replicates and pairwise comparisons are not assumed independent.",
                             "Caller-supplied observations and evidence references are not verified by this metric."])
    return json.dumps(body, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
