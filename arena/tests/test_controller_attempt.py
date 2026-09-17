import hashlib
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from iah_arena.artifacts import ArtifactProvenance
from iah_arena.budgets import BudgetLedger, BudgetLimits
from iah_arena.controller import ArenaController
from iah_arena.providers import DecisionContext, ProviderTurn, ScriptedProvider, ToolCall


class ArenaControllerAttemptTests(unittest.TestCase):
    def test_scripted_provider_completes_an_accepted_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed = root / "seed"
            seed.mkdir()
            (seed / "solver.txt").write_text("primitive\n", encoding="utf-8")
            controller = ArenaController(root / "state", artifact_dir=root / "artifacts")
            controller.initialize_lineage("lineage-a", origin="test")
            controller.initialize_workspace("lineage-a", seed)
            budget = BudgetLedger(BudgetLimits(5, 100, 100, 100, 10))
            provider = ScriptedProvider(
                (
                    ProviderTurn(
                        tool_calls=(
                            ToolCall(
                                "write",
                                "write_file",
                                {
                                    "path": "solver.txt", "content": "improved\n",
                                    "expected_sha256": hashlib.sha256(
                                        (seed / "solver.txt").read_bytes()
                                    ).hexdigest(),
                                },
                            ),
                        )
                    ),
                    ProviderTurn(
                        tool_calls=(ToolCall("test", "run_public_tests", {}),)
                    ),
                    ProviderTurn(
                        tool_calls=(
                            ToolCall(
                                "submit",
                                "submit_candidate",
                                {
                                    "claim": {
                                        "bottleneck": "primitive marker",
                                        "hypothesis": "replacement improves fitness",
                                        "changes": ["replace marker"],
                                        "expected_effect": "pass evaluator",
                                        "risks": [],
                                    }
                                },
                            ),
                        )
                    ),
                )
            )
            context = DecisionContext(
                lineage_id="lineage-a",
                epoch=1,
                generation=0,
                attempt=1,
                objective={},
                metrics={},
                budget_remaining=asdict(budget.remaining()),
                workspace_summary={},
            )
            result = controller.run_attempt(
                lineage_id="lineage-a",
                epoch=1,
                attempt=1,
                provider=provider,
                context=context,
                budget=budget,
                public_test_runner=lambda workspace: {
                    "passed": (workspace / "solver.txt").read_text(encoding="utf-8")
                    == "improved\n"
                },
                evaluator=lambda workspace: {"accepted": True, "fitness": 1.0},
                artifact_provenance=ArtifactProvenance(
                    lineage_id="lineage-a",
                    epoch=1,
                    generation=1,
                    attempt=1,
                    parent_generation=0,
                    task_id="test-task",
                    task_version="v1",
                    evaluator_version="v1",
                    curriculum_digest="c" * 64,
                    environment_digest="sha256:" + "d" * 64,
                    arena_commit="test",
                    random_seed=1,
                    optimizer_id="scripted/scripted-v1",
                ),
            )

            self.assertTrue(result.accepted)
            self.assertEqual(result.generation, 1)
            self.assertEqual(provider.calls, 3)
            self.assertIsNotNone(result.artifact_id)
            self.assertEqual(controller.artifact_store.verify(result.artifact_id), 1)
            self.assertEqual(
                (controller.workspace_manager("lineage-a").current_files() / "solver.txt")
                .read_text(encoding="utf-8"),
                "improved\n",
            )
            self.assertGreater(controller.verify_lineage("lineage-a"), 10)


if __name__ == "__main__":
    unittest.main()
