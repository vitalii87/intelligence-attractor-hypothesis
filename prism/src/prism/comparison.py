"""Explicit compatibility checks, not an assertion of scientific comparability."""
from .models import EvaluationContext


def incompatibilities(left: EvaluationContext, right: EvaluationContext, *, resource_metric=False) -> tuple[str, ...]:
    reasons = []
    for field in ("task_id", "suite_sha256", "evaluator_version", "protocol_sha256"):
        a, b = getattr(left, field), getattr(right, field)
        if not a or not b:
            reasons.append(f"missing:{field}")
        elif a != b:
            reasons.append(f"different:{field}")
    if resource_metric:
        if not left.environment_id or not right.environment_id:
            reasons.append("missing:environment_id")
        elif left.environment_id != right.environment_id:
            reasons.append("different:environment_id")
    return tuple(reasons)
