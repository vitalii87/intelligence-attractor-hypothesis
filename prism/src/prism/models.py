"""Minimal interchange contracts. Unknown measurements are explicit."""
from dataclasses import dataclass
from enum import Enum
import math


class Status(str, Enum):
    MEASURED = "measured"
    NOT_MEASURED = "not_measured"
    INCOMPATIBLE = "incompatible"
    ERROR = "error"


@dataclass(frozen=True)
class ArtifactRef:
    location: str
    sha256: str

    def __post_init__(self):
        if not self.location or len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256):
            raise ValueError("artifact requires a location and lowercase SHA-256")


@dataclass(frozen=True)
class EntityVersion:
    entity_id: str
    version_id: str
    artifacts: tuple[ArtifactRef, ...] = ()
    parent_version_id: str | None = None
    origin_label: str | None = None

    def __post_init__(self):
        if not self.entity_id or not self.version_id:
            raise ValueError("entity and version IDs are required")


@dataclass(frozen=True)
class EvaluationContext:
    task_id: str
    suite_sha256: str
    evaluator_version: str
    protocol_sha256: str
    environment_id: str | None = None


@dataclass(frozen=True)
class Measurement:
    metric_id: str
    metric_version: str
    entity_ids: tuple[str, ...]
    status: Status
    value: float | None = None
    unit: str | None = None
    reason: str | None = None
    evidence: tuple[ArtifactRef, ...] = ()

    def __post_init__(self):
        if not self.metric_id or not self.metric_version or not self.entity_ids:
            raise ValueError("metric identity and subjects required")
        if not isinstance(self.status, Status):
            raise ValueError("status must be a Status")
        if self.status is Status.MEASURED:
            if type(self.value) not in (int, float) or not math.isfinite(self.value):
                raise ValueError("measured results require a finite numeric value")
        elif self.value is not None or not self.reason:
            raise ValueError("unmeasured results require a reason and no numeric value")
