"""Stable JSON serialization of contract objects; no interpretation generation."""
from dataclasses import asdict
import json
from . import __version__
from .models import Measurement


def render_json(measurements: tuple[Measurement, ...]) -> str:
    return json.dumps({"schema_version": "prism-report-v1", "prism_version": __version__,
                       "measurements": [asdict(item) for item in measurements]},
                      sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
