from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .artifacts import ArtifactProvenance, ArtifactStore
from .budgets import BudgetLedger
from .domain import ArenaEvent, EventType
from .events import JsonlEventStore
from .providers import DecisionContext, ProviderAdapter
from .sessions import DecisionSessionRunner, SessionLimits, SessionOutcome
from .tools import EditBudget, PublicTestRunner, WorkspaceToolExecutor
from .workspace import LineageWorkspaceManager


Evaluator = Callable[[Path], Mapping[str, Any]]


@dataclass(frozen=True, slots=True)
class AttemptRunResult:
    accepted: bool
    generation: int
    evaluation: Mapping[str, Any]
    session: SessionOutcome
    files_path: Path
    artifact_id: str | None = None


class ArenaController:
    """Trusted orchestration boundary for one experimental lineage."""

    def __init__(self, state_dir: Path, *, artifact_dir: Path | None = None) -> None:
        self.state_dir = Path(state_dir)
        self.artifact_store = None if artifact_dir is None else ArtifactStore(artifact_dir)

    def event_store(self, lineage_id: str) -> JsonlEventStore:
        return JsonlEventStore(self.state_dir / "lineages" / lineage_id / "events.jsonl")

    def workspace_manager(self, lineage_id: str) -> LineageWorkspaceManager:
        return LineageWorkspaceManager(self.state_dir, lineage_id)

    def initialize_lineage(
        self,
        lineage_id: str,
        *,
        origin: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        store = self.event_store(lineage_id)
        if store.path.exists() and store.validate() > 0:
            raise FileExistsError(f"lineage already exists: {lineage_id}")
        payload = {"origin": origin, "metadata": dict(metadata or {})}
        return store.append(
            ArenaEvent(
                lineage_id=lineage_id,
                event_type=EventType.LINEAGE_CREATED,
                payload=payload,
            )
        )

    def initialize_workspace(self, lineage_id: str, seed_workspace: Path) -> Path:
        files_path = self.workspace_manager(lineage_id).initialize(seed_workspace)
        self.event_store(lineage_id).append(
            ArenaEvent(
                lineage_id=lineage_id,
                event_type=EventType.WORKSPACE_INITIALIZED,
                payload={"generation": 0, "source": "seed"},
            )
        )
        return files_path

    def run_attempt(
        self,
        *,
        lineage_id: str,
        epoch: int,
        attempt: int,
        provider: ProviderAdapter,
        context: DecisionContext,
        budget: BudgetLedger,
        public_test_runner: PublicTestRunner,
        evaluator: Evaluator,
        limits: SessionLimits = SessionLimits(),
        artifact_provenance: ArtifactProvenance | None = None,
        edit_budget: EditBudget | None = None,
        max_file_bytes: int = 256_000,
        max_workspace_bytes: int = 2_000_000,
    ) -> AttemptRunResult:
        manager = self.workspace_manager(lineage_id)
        current_generation = manager.current_generation()
        expected_context = (lineage_id, epoch, current_generation, attempt)
        actual_context = (
            context.lineage_id,
            context.epoch,
            context.generation,
            context.attempt,
        )
        if actual_context != expected_context:
            raise ValueError(
                "decision context does not match requested lineage, epoch, generation, and attempt"
            )
        if artifact_provenance is not None:
            if self.artifact_store is None:
                raise ValueError("artifact_provenance requires an artifact store")
            expected_provenance = (
                lineage_id,
                epoch,
                current_generation + 1,
                attempt,
                current_generation,
            )
            actual_provenance = (
                artifact_provenance.lineage_id,
                artifact_provenance.epoch,
                artifact_provenance.generation,
                artifact_provenance.attempt,
                artifact_provenance.parent_generation,
            )
            if actual_provenance != expected_provenance:
                raise ValueError("artifact provenance does not match the requested attempt")
        workspace = manager.begin_attempt(epoch=epoch, attempt=attempt)
        generation = workspace.lifecycle.parent_generation
        store = self.event_store(lineage_id)

        def emit(event_type: EventType, payload: Mapping[str, Any]) -> None:
            store.append(
                ArenaEvent(
                    lineage_id=lineage_id,
                    event_type=event_type,
                    payload=payload,
                    epoch=epoch,
                    generation=generation,
                    attempt=attempt,
                )
            )

        emit(EventType.ATTEMPT_STARTED, {"parent_generation": generation})
        executor = WorkspaceToolExecutor(
            workspace.files_path,
            public_test_runner=public_test_runner,
            edit_budget=edit_budget,
            max_file_bytes=max_file_bytes,
            max_workspace_bytes=max_workspace_bytes,
        )
        runner = DecisionSessionRunner(
            provider=provider,
            executor=executor,
            budget=budget,
            event_sink=emit,
            limits=limits,
        )

        try:
            outcome = runner.run(context)
        except Exception as error:
            archived = manager.reject(workspace, reason=f"arena failure: {error}")
            emit(
                EventType.ARENA_FAILURE,
                {"error_type": type(error).__name__, "message": str(error)},
            )
            emit(EventType.CANDIDATE_REJECTED, {"reason": archived.lifecycle.reason})
            raise

        if outcome.aborted:
            archived = manager.abort(workspace, reason=outcome.reason or "provider aborted")
            emit(EventType.ATTEMPT_ABORTED, {"reason": archived.lifecycle.reason})
            return AttemptRunResult(False, generation, {}, outcome, archived.files_path)

        if not outcome.submitted:
            archived = manager.reject(workspace, reason=outcome.reason or "not submitted")
            emit(EventType.CANDIDATE_REJECTED, {"reason": archived.lifecycle.reason})
            return AttemptRunResult(False, generation, {}, outcome, archived.files_path)

        workspace = manager.submit(workspace)
        emit(
            EventType.CANDIDATE_SUBMITTED,
            {"summary": outcome.reason, "claim": outcome.claim},
        )
        try:
            evaluation = dict(evaluator(workspace.files_path))
        except Exception as error:
            archived = manager.reject(workspace, reason=f"evaluator failure: {error}")
            emit(
                EventType.ARENA_FAILURE,
                {"error_type": type(error).__name__, "message": str(error)},
            )
            emit(EventType.CANDIDATE_REJECTED, {"reason": archived.lifecycle.reason})
            raise
        accepted = evaluation.get("accepted")
        if not isinstance(accepted, bool):
            manager.reject(workspace, reason="invalid evaluator result")
            emit(
                EventType.ARENA_FAILURE,
                {"error_type": "ValueError", "message": "evaluator must return boolean accepted"},
            )
            raise ValueError("evaluator must return boolean 'accepted'")
        emit(EventType.CANDIDATE_EVALUATED, evaluation)

        if accepted:
            artifact_id = None
            if artifact_provenance is not None:
                try:
                    manifest = self.artifact_store.capture_directory(
                        workspace.files_path,
                        artifact_type="accepted_candidate",
                        provenance=artifact_provenance,
                    )
                    artifact_id = manifest.artifact_id
                except Exception as error:
                    archived = manager.reject(workspace, reason=f"artifact failure: {error}")
                    emit(
                        EventType.ARENA_FAILURE,
                        {"error_type": type(error).__name__, "message": str(error)},
                    )
                    emit(EventType.CANDIDATE_REJECTED, {"reason": archived.lifecycle.reason})
                    raise
            promoted = manager.accept(workspace)
            next_generation = promoted.lifecycle.parent_generation + 1
            if artifact_id is not None:
                emit(
                    EventType.ARTIFACT_CAPTURED,
                    {"artifact_id": artifact_id, "generation": next_generation},
                )
            emit(EventType.CANDIDATE_ACCEPTED, {"generation": next_generation})
            return AttemptRunResult(
                True,
                next_generation,
                evaluation,
                outcome,
                promoted.files_path,
                artifact_id,
            )

        archived = manager.reject(
            workspace,
            reason=str(evaluation.get("reason", "evaluator rejected candidate")),
        )
        emit(EventType.CANDIDATE_REJECTED, {"reason": archived.lifecycle.reason})
        return AttemptRunResult(False, generation, evaluation, outcome, archived.files_path)

    def verify_lineage(self, lineage_id: str) -> int:
        return self.event_store(lineage_id).validate()
