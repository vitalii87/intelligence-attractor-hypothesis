from pathlib import Path
import tempfile
import unittest

from iah_arena.iteration_rate import IterationRate, IterationRateLimited, reserve_iteration


class RateTests(unittest.TestCase):
    def test_rolling_window_restart_and_no_catchup(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rate.json"
            rate = IterationRate(2, 60)
            reserve_iteration(path, rate, now=100)
            reserve_iteration(path, rate, now=110)
            with self.assertRaises(IterationRateLimited) as error:
                reserve_iteration(path, rate, now=159)
            self.assertEqual(error.exception.retry_at, 160)
            reserve_iteration(path, rate, now=160)
            with self.assertRaises(IterationRateLimited):
                reserve_iteration(path, rate, now=160)
            reserve_iteration(path, rate, now=10000)
            reserve_iteration(path, rate, now=10000)
            with self.assertRaises(IterationRateLimited):
                reserve_iteration(path, rate, now=10000)

    def test_clock_and_settings_changes_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rate.json"
            reserve_iteration(path, IterationRate(1, 60), now=100)
            with self.assertRaises(ValueError):
                reserve_iteration(path, IterationRate(1, 60), now=99)
            with self.assertRaises(ValueError):
                reserve_iteration(path, IterationRate(2, 60), now=101)
