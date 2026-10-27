"""Read-only import boundary; adapters must not execute imported artifacts."""
from pathlib import Path
from typing import Protocol
from ..models import EntityVersion


class ArtifactAdapter(Protocol):
    adapter_id: str
    adapter_version: str

    def load(self, source: Path) -> tuple[EntityVersion, ...]: ...
