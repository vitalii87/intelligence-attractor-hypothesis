from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from .budgets import BudgetLedger, BudgetLimits
from .controller import ArenaController
from .docker_runtime import DockerRuntime
from .experiment import ExperimentRunManager
from .providers import DecisionContext, ProviderTurn, ScriptedProvider, ToolCall
from .runtime import RuntimeLimits, RuntimeRequest, RuntimeRole
from .run_config import RunConfigLoader
from .sessions import SessionLimits
from .telemetry import TelemetryExporter


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="iah-arena")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init-lineage", help="create an empty lineage event chain")
    init.add_argument("--state-dir", type=Path, required=True)
    init.add_argument("--lineage-id", required=True)
    init.add_argument("--origin", required=True)

    verify = subparsers.add_parser("verify-events", help="verify a lineage event hash chain")
    verify.add_argument("--state-dir", type=Path, required=True)
    verify.add_argument("--lineage-id", required=True)

    dry_run = subparsers.add_parser(
        "dry-run",
        help="exercise one complete upgrade attempt with a deterministic fake provider",
    )
    dry_run.add_argument("--state-dir", type=Path, required=True)
    dry_run.add_argument("--lineage-id", default="dry-run-001")

    task_demo = subparsers.add_parser(
        "task-demo", help="run scripted isolated lineages on a real arithmetic task (not an IAH experiment)",
    )
    task_demo.add_argument("--task", choices=("integer-sum",), default="integer-sum")
    task_demo.add_argument("--output-dir", type=Path, required=True)
    engine = task_demo.add_mutually_exclusive_group(required=True)
    engine.add_argument("--trusted-local", action="store_true", help="execute only exact bundled fixtures without Docker")
    engine.add_argument("--image", help="pinned Docker image digest containing python3")

    docker_check = subparsers.add_parser(
        "docker-check",
        help="run the toolchain report inside a pinned polyglot image",
    )
    docker_check.add_argument("--image", required=True)
    docker_check.add_argument("--docker-binary", default="docker")
    docker_check.add_argument("--container-user", default="1000:1000")

    export = subparsers.add_parser(
        "export-telemetry",
        help="export validated cross-lineage events and numeric evaluation metrics",
    )
    export.add_argument("--state-dir", type=Path, required=True)
    export.add_argument("--output-dir", type=Path, required=True)
    export.add_argument("--lineage-id", action="append", required=True)

    create_run = subparsers.add_parser(
        "create-run",
        help="freeze a TOML run configuration into a new experiment run",
    )
    create_run.add_argument("--state-dir", type=Path, required=True)
    create_run.add_argument("--config", type=Path, required=True)

    status = subparsers.add_parser("run-status", help="show verified experiment-run state")
    _add_run_arguments(status)

    start_run = subparsers.add_parser("start-run", help="enter the optimization phase")
    _add_run_arguments(start_run, revision=True)

    close_run = subparsers.add_parser(
        "close-run-optimization",
        help="irreversibly close the optimization phase",
    )
    _add_run_arguments(close_run, revision=True)

    open_holdout = subparsers.add_parser(
        "open-run-holdout",
        help="open one-shot final-holdout access",
    )
    _add_run_arguments(open_holdout, revision=True)

    recover = subparsers.add_parser(
        "recover-run-state",
        help="restore state.json from the last hash-chained state commit",
    )
    _add_run_arguments(recover)

    reserve = subparsers.add_parser(
        "reserve-holdout",
        help="reserve one final artifact for a lineage",
    )
    _add_run_arguments(reserve, revision=True)
    reserve.add_argument("--lineage-id", required=True)
    reserve.add_argument("--artifact-id", required=True)

    record = subparsers.add_parser(
        "record-holdout",
        help="record the hash of a reserved final-holdout result",
    )
    _add_run_arguments(record, revision=True)
    record.add_argument("--lineage-id", required=True)
    record.add_argument("--reservation-token", required=True)
    record.add_argument("--result-sha256", required=True)
    return parser


def _add_run_arguments(parser: argparse.ArgumentParser, *, revision: bool = False) -> None:
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--experiment-id", required=True)
    if revision:
        parser.add_argument("--expected-revision", type=int, required=True)


def _dry_run(controller: ArenaController, lineage_id: str) -> int:
    with TemporaryDirectory(prefix="iah-seed-") as temporary:
        seed = Path(temporary)
        (seed / "solver.txt").write_text("primitive\n", encoding="utf-8")
        controller.initialize_lineage(lineage_id, origin="scripted-dry-run")
        controller.initialize_workspace(lineage_id, seed)
        seed_sha256 = hashlib.sha256((seed / "solver.txt").read_bytes()).hexdigest()

    provider = ScriptedProvider(
        (
            ProviderTurn(tool_calls=(ToolCall("1", "read_file", {"path": "solver.txt"}),)),
            ProviderTurn(
                tool_calls=(
                    ToolCall(
                        "2",
                        "write_file",
                        {
                            "path": "solver.txt", "content": "improved\n",
                            "expected_sha256": seed_sha256,
                        },
                    ),
                )
            ),
            ProviderTurn(tool_calls=(ToolCall("3", "run_public_tests", {}),)),
            ProviderTurn(
                tool_calls=(
                    ToolCall(
                        "4",
                        "submit_candidate",
                        {
                            "claim": {
                                "bottleneck": "primitive marker",
                                "hypothesis": "replacement satisfies the dry-run evaluator",
                                "changes": ["replace solver marker"],
                                "expected_effect": "public and selection checks pass",
                                "risks": [],
                            }
                        },
                    ),
                )
            ),
        )
    )
    limits = BudgetLimits(8, 10_000, 10_000, 100_000, 60)
    budget = BudgetLedger(limits)
    context = DecisionContext(
        lineage_id=lineage_id,
        epoch=1,
        generation=0,
        attempt=1,
        objective={"goal": "replace the primitive marker"},
        metrics={"public_passed": False},
        budget_remaining=asdict(budget.remaining()),
        workspace_summary={"known_files": ["solver.txt"]},
    )

    def public_tests(workspace: Path) -> dict[str, object]:
        passed = (workspace / "solver.txt").read_text(encoding="utf-8") == "improved\n"
        return {"passed": passed, "checks": 1}

    def evaluator(workspace: Path) -> dict[str, object]:
        accepted = (workspace / "solver.txt").read_text(encoding="utf-8") == "improved\n"
        return {"accepted": accepted, "fitness": 1.0 if accepted else 0.0}

    result = controller.run_attempt(
        lineage_id=lineage_id,
        epoch=1,
        attempt=1,
        provider=provider,
        context=context,
        budget=budget,
        public_test_runner=public_tests,
        evaluator=evaluator,
        limits=SessionLimits(max_provider_turns=6, max_tool_calls=10),
    )
    event_count = controller.verify_lineage(lineage_id)
    print(
        f"dry-run accepted={result.accepted} generation={result.generation} "
        f"provider_turns={result.session.provider_turns} events={event_count}"
    )
    return 0 if result.accepted else 1


def _docker_check(image: str, docker_binary: str, container_user: str) -> int:
    runtime = DockerRuntime(
        image,
        docker_binary=docker_binary,
        container_user=container_user,
    )
    limits = RuntimeLimits(
        cpus=1,
        memory_mb=512,
        pids=32,
        timeout_seconds=30,
        tmpfs_mb=64,
        max_output_bytes=64_000,
    )
    request = RuntimeRequest(
        ("iah-toolchain-report",),
        RuntimeRole.JUDGE,
        workspace_read_only=True,
    )
    with TemporaryDirectory(prefix="iah-docker-check-") as temporary:
        result = runtime.run(Path(temporary), request, limits)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    print(
        f"docker-check succeeded={result.succeeded} timed_out={result.timed_out} "
        f"duration_ms={result.duration_ms}"
    )
    return 0 if result.succeeded else 1


def main() -> int:
    args = _parser().parse_args()
    if args.command == "task-demo":
        from .demo import TrustedDemoRuntime, run_task_demo
        from .fitness import FitnessPolicy, MetricDirection, MetricSpec
        from .tasks.integer_sum import IntegerSumTask, SEEDS, SOLUTIONS

        if args.trusted_local:
            runtime = TrustedDemoRuntime(frozenset((*SEEDS.values(), *SOLUTIONS.values())))
            environment = "trusted-fixtures-only; no container isolation"
        else:
            runtime = DockerRuntime(args.image)
            environment = args.image
        try:
            summary = run_task_demo(
                IntegerSumTask(runtime),
                {name: (seed, SOLUTIONS[name]) for name, seed in SEEDS.items()},
                args.output_dir, environment=environment,
                policy=FitnessPolicy((MetricSpec("correct_fraction", MetricDirection.MAXIMIZE),)),
            )
        except (OSError, ValueError) as error:
            print(f"task-demo: {error}")
            return 1
        return 0 if summary["success"] else 1
    if args.command == "docker-check":
        return _docker_check(args.image, args.docker_binary, args.container_user)

    if args.command == "export-telemetry":
        exported = TelemetryExporter(args.state_dir).export_bundle(
            args.lineage_id,
            args.output_dir,
        )
        print(
            f"exported id={exported.export_id} events={exported.event_rows} "
            f"metrics={exported.metric_rows} path={exported.path}"
        )
        return 0
    if args.command == "create-run":
        loaded = RunConfigLoader().load(args.config)
        manager = ExperimentRunManager(args.state_dir, loaded.manifest.experiment_id)
        state = manager.create(loaded.manifest)
        print(
            f"created experiment={loaded.manifest.experiment_id} "
            f"manifest={loaded.manifest.digest} revision={state.revision}"
        )
        return 0
    if args.command in {
        "run-status",
        "start-run",
        "close-run-optimization",
        "open-run-holdout",
        "recover-run-state",
        "reserve-holdout",
        "record-holdout",
    }:
        manager = ExperimentRunManager(args.state_dir, args.experiment_id)
        if args.command == "run-status":
            print(json.dumps(manager.state().as_dict(), indent=2, sort_keys=True))
            return 0
        if args.command == "start-run":
            state = manager.start_optimization(expected_revision=args.expected_revision)
        elif args.command == "close-run-optimization":
            state = manager.close_optimization(expected_revision=args.expected_revision)
        elif args.command == "open-run-holdout":
            state = manager.open_holdout(expected_revision=args.expected_revision)
        elif args.command == "recover-run-state":
            state = manager.recover_state()
        elif args.command == "reserve-holdout":
            reservation = manager.reserve_holdout(
                args.lineage_id,
                args.artifact_id,
                expected_revision=args.expected_revision,
            )
            print(json.dumps(reservation.as_dict(), indent=2, sort_keys=True))
            return 0
        else:
            state = manager.record_holdout_result(
                args.lineage_id,
                args.reservation_token,
                args.result_sha256,
                expected_revision=args.expected_revision,
            )
        print(json.dumps(state.as_dict(), indent=2, sort_keys=True))
        return 0

    controller = ArenaController(args.state_dir)

    if args.command == "init-lineage":
        event_hash = controller.initialize_lineage(args.lineage_id, origin=args.origin)
        print(f"created {args.lineage_id} event_hash={event_hash}")
        return 0

    if args.command == "verify-events":
        count = controller.verify_lineage(args.lineage_id)
        print(f"verified {args.lineage_id} events={count}")
        return 0

    if args.command == "dry-run":
        return _dry_run(controller, args.lineage_id)

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
