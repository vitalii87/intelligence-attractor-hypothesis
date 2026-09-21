import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from iah_arena.preflight import check_iterations
from iah_arena.docker_runtime import DockerRuntimeError

ROOT = Path(__file__).resolve().parents[1]


class PreflightTests(unittest.TestCase):
    def test_scripted_no_network_no_files(self):
        with patch("urllib.request.OpenerDirector.open", side_effect=AssertionError("network")), \
             patch("iah_arena.preflight.DockerRuntime.check_ready", side_effect=AssertionError("docker")):
            report = check_iterations(ROOT / "iteration.example.toml")
        self.assertTrue(report["ready"])
        self.assertFalse(report["provider_contacted"])
        self.assertEqual(report["limits"]["aggregate_configured_cost_microusd"], 0)

    def test_missing_and_invalid_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            self.assertFalse(check_iterations(path)["ready"])
            path.write_text('secret-value = "secret-value"')
            report = check_iterations(path)
            self.assertFalse(report["ready"])
            self.assertNotIn("secret-value", json.dumps(report))

    def test_api_readiness_and_budget_arithmetic(self):
        raw = (ROOT / "openai.example.toml").read_text().replace('"openai/"', '"openai/test-model"')
        raw = raw.replace('input_microusd_per_million = 0', 'input_microusd_per_million = 1000000')
        raw = raw.replace('output_microusd_per_million = 0', 'output_microusd_per_million = 2000000')
        with tempfile.TemporaryDirectory() as tmp, patch("urllib.request.OpenerDirector.open", side_effect=AssertionError("network")), \
             patch("iah_arena.preflight.DockerRuntime.check_ready") as docker, patch.dict(os.environ, {}, clear=True):
            path = Path(tmp) / "config.toml"
            path.write_text(raw)
            missing = check_iterations(path)
            self.assertFalse(missing["ready"])
            os.environ["OPENAI_API_KEY"] = "test-secret-must-not-appear"
            ready = check_iterations(path)
            self.assertTrue(ready["ready"])
            self.assertEqual(ready["limits"]["aggregate_configured_cost_microusd"], 3000000)
            self.assertEqual(ready["limits"]["full_request_cost_microusd"], 38000)
            self.assertEqual(ready["limits"]["full_requests_fitting_attempt"], 6)
            self.assertNotIn("test-secret-must-not-appear", json.dumps(ready))
            docker.side_effect = DockerRuntimeError("internal-secret")
            failed = check_iterations(path)
            self.assertFalse(failed["ready"])
            self.assertNotIn("internal-secret", json.dumps(failed))
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_unfilled_template_is_not_ready(self):
        self.assertFalse(check_iterations(ROOT / "openai.example.toml")["ready"])
