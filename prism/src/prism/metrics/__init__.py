"""Metric extension contracts. Exact behavioral measurement is available in behavior.py."""
from typing import Protocol
from ..models import EntityVersion, EvaluationContext, Measurement


class PairMetric(Protocol):
    metric_id: str
    metric_version: str

    def compare(self, left: EntityVersion, right: EntityVersion,
                context: EvaluationContext) -> Measurement: ...
