"""Tests adaptateur LangGraph-shaped — mock only, langgraph optionnel."""

from __future__ import annotations

import unittest

from idc import MockBackend
from idc.langgraph_adapter import (
    LANGGRAPH_INSTALL_HINT,
    IdcGraphRunner,
    compile_langgraph,
    deliberation_node,
    initial_state,
    require_langgraph,
    should_continue,
)
from idc.mock_backend import UNCERTAIN, VERBOSE


class TestIdcGraphRunner(unittest.TestCase):
    def test_idc_stops_earlier_than_baseline(self) -> None:
        b_idc = MockBackend(VERBOSE)
        b_base = MockBackend(VERBOSE)
        idc = IdcGraphRunner(backend=b_idc, use_stop_rule=True, gain_fn=b_idc.gain_for_step)
        base = IdcGraphRunner(backend=b_base, use_stop_rule=False, gain_fn=b_base.gain_for_step)
        r_idc = idc.run("tâche verbose")
        r_base = base.run("tâche verbose")
        self.assertLess(r_idc.steps, r_base.steps)
        self.assertGreaterEqual(r_idc.resource_final, r_base.resource_final)
        self.assertTrue(r_idc.stopped_early)
        self.assertEqual(r_idc.mode, "idc")
        self.assertEqual(r_base.mode, "baseline")

    def test_node_loop_marks_stop(self) -> None:
        b = MockBackend(VERBOSE)
        cfg = IdcGraphRunner(backend=b, use_stop_rule=True, gain_fn=b.gain_for_step).config()
        state = initial_state("x", use_stop_rule=True)
        for _ in range(8):
            state = deliberation_node(state, cfg)
            if should_continue(state) == "end":
                break
        self.assertTrue(state["stopped"])
        self.assertLess(state["step"], 8)
        self.assertGreaterEqual(len(state["journal_entries"]), 2)

    def test_uncertain_admits_ignorance(self) -> None:
        b = MockBackend(UNCERTAIN)
        r = IdcGraphRunner(
            backend=b, use_stop_rule=True, gain_fn=b.gain_for_step
        ).run("question sans source")
        self.assertTrue(r.admitted_ignorance)

    def test_invoke_api(self) -> None:
        b = MockBackend(VERBOSE)
        out = IdcGraphRunner(backend=b, use_stop_rule=True, gain_fn=b.gain_for_step).invoke(
            {"task": "demo", "resource": 100.0}
        )
        self.assertIn("answer", out)
        self.assertTrue(out["stopped"])


class TestLangGraphOptional(unittest.TestCase):
    def test_require_langgraph_message_or_import(self) -> None:
        try:
            StateGraph, END = require_langgraph()
            self.assertIsNotNone(StateGraph)
            self.assertIsNotNone(END)
        except ImportError as exc:
            self.assertIn("idc-wrapper[langgraph]", str(exc))
            self.assertIn("langgraph", str(exc).lower())

    def test_compile_langgraph_or_skip(self) -> None:
        b = MockBackend(VERBOSE)
        try:
            graph = compile_langgraph(
                backend=b,
                use_stop_rule=True,
                gain_fn=b.gain_for_step,
            )
        except ImportError as exc:
            self.assertIn(LANGGRAPH_INSTALL_HINT.split(".")[0], str(exc))
            self.skipTest("langgraph non installé — OK pour CI")
            return
        # Si langgraph est présent : un invoke court doit s'arrêter tôt sous IDC.
        out = graph.invoke(
            {
                "task": "demo langgraph",
                "answer": "",
                "partial": "",
                "step": 0,
                "resource": 100.0,
                "tokens_approx_total": 0,
                "cost_total": 0.0,
                "stopped": False,
                "admitted_ignorance": False,
                "journal_entries": [],
                "last_chunk": "",
                "last_gain": 0.0,
                "max_gain_seen": 0.0,
                "any_useful": False,
                "use_stop_rule": True,
            }
        )
        self.assertTrue(out.get("stopped"))
        self.assertLess(int(out.get("step", 99)), 8)


if __name__ == "__main__":
    unittest.main()
