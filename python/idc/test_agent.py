"""Tests unitaires (stdlib unittest) — mock only, pas de clé API."""

from __future__ import annotations

import unittest

from idc import IdcAgent, MockBackend
from idc.mock_backend import SUPPORT_CLIENT, UNCERTAIN, VERBOSE


class TestIdcVsBaseline(unittest.TestCase):
    def test_idc_stops_earlier_than_baseline_on_verbose(self) -> None:
        b_idc = MockBackend(VERBOSE)
        b_base = MockBackend(VERBOSE)
        idc = IdcAgent(backend=b_idc, use_stop_rule=True, gain_fn=b_idc.gain_for_step)
        base = IdcAgent(backend=b_base, use_stop_rule=False, gain_fn=b_base.gain_for_step)
        r_idc = idc.run("tâche verbose")
        r_base = base.run("tâche verbose")
        self.assertLess(r_idc.steps, r_base.steps)
        self.assertGreaterEqual(r_idc.resource_final, r_base.resource_final)
        self.assertGreaterEqual(r_idc.steps, 2)
        self.assertLessEqual(r_idc.steps, 4)

    def test_journal_grows_monotonically(self) -> None:
        b = MockBackend(SUPPORT_CLIENT)
        agent = IdcAgent(backend=b, use_stop_rule=True, gain_fn=b.gain_for_step)
        r = agent.run("où est mon colis ?")
        self.assertGreaterEqual(len(r.journal), 2)
        steps = [e.step for e in r.journal.entries]
        self.assertEqual(steps, list(range(1, len(steps) + 1)))

    def test_uncertain_admits_ignorance_under_idc(self) -> None:
        b = MockBackend(UNCERTAIN)
        agent = IdcAgent(
            backend=b,
            resource=100.0,
            critical_threshold=15.0,
            cost_per_token=0.8,
            max_steps=8,
            use_stop_rule=True,
            gain_fn=b.gain_for_step,
        )
        r = agent.run("question sans source")
        self.assertTrue(r.admitted_ignorance)
        self.assertLess(r.steps, 8)


if __name__ == "__main__":
    unittest.main()
