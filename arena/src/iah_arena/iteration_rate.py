"""Durable rolling-window launch rate; does not run a background scheduler."""
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import time

from .locking import FileLock
from .model_gateway import _hash, _save


class IterationRateLimited(RuntimeError):
    def __init__(self, retry_at):
        self.retry_at = retry_at
        super().__init__(f"iteration rate limit reached; retry at Unix UTC {retry_at}")


@dataclass(frozen=True)
class IterationRate:
    iterations: int
    period_seconds: int

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in asdict(self).values()):
            raise ValueError("rate values must be positive integers")


def reserve_iteration(path: Path, rate: IterationRate, *, now=None):
    instant = time.time() if now is None else now
    if type(instant) not in (int, float) or not math.isfinite(instant) or instant < 0:
        raise ValueError("invalid time")
    path = Path(path)
    with FileLock(path.with_suffix(".lock")):
        if path.exists():
            envelope = json.loads(path.read_text(encoding="utf-8"))
            state = envelope["state"]
            if envelope["sha256"] != _hash(state) or state["rate"] != asdict(rate):
                raise ValueError("rate state or configuration changed")
            if instant < state["last_seen"]:
                raise ValueError("clock moved backwards; rate reservation refused")
        else:
            state = {"rate": asdict(rate), "last_seen": instant, "starts": []}
        starts = [t for t in state["starts"] if t > instant - rate.period_seconds]
        state.update(starts=starts, last_seen=instant)
        if len(starts) >= rate.iterations:
            _save(path, state)
            raise IterationRateLimited(starts[0] + rate.period_seconds)
        starts.append(instant)
        _save(path, state)
