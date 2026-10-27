"""Content-addressed import manifest. Does not infer suites or scientific metrics."""
from dataclasses import asdict
import json
from . import __version__
from .adapters.arena import canonical, digest, ImportFailure


def dataset_manifest(imported):
    records = [asdict(item) for item in imported]
    records.sort(key=lambda item: (item["entity"]["entity_id"], item["entity"]["version_id"]))
    identities = [(r["entity"]["entity_id"], r["entity"]["version_id"]) for r in records]
    if len(identities) != len(set(identities)):
        raise ImportFailure("duplicate entity version")
    body = {"schema_version": "prism-dataset-v1", "prism_version": __version__,
            "adapter": "arena-artifact-store/1", "artifacts": records,
            "limitations": ["Artifact checksums do not authenticate their producer.",
                            "No suite alignment, scientific metrics or causal interpretation inferred."]}
    return {"dataset_sha256": digest(canonical(body)), **body}


def render_dataset(imported):
    return json.dumps(dataset_manifest(imported), indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)
