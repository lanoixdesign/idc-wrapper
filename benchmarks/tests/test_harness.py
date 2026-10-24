"""Tests légers du harness (sans réseau, sans clé API)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from idc_bench.client import ScriptedBackend, _parse_duration  # noqa: E402
from idc_bench.core import CONDITIONS, IGNORANCE_MSG, Params, auto_match, jaccard, run_task  # noqa: E402
from idc_bench.judge import build_judge_prompt, parse_judgment  # noqa: E402
from idc_bench.stats import cluster_bootstrap, mcnemar_exact  # noqa: E402

LONG = ("Canberra est la capitale fédérale de l'Australie, choisie en 1908 comme compromis "
        "entre Sydney et Melbourne, et siège du Parlement depuis 1927.")
TASK = {"id": "t1", "category": "factual", "mode": "single", "prompt": "Capitale de l'Australie ?",
        "expected_behavior": "answer", "reference": "Canberra", "match": [["canberra"]]}


class TestCore(unittest.TestCase):
    def test_baseline_runs_to_cap_and_flags_loop(self):
        r = run_task(ScriptedBackend([LONG]), TASK, CONDITIONS["sans_idc"], Params())
        self.assertEqual(r["steps"], 4)
        self.assertTrue(r["hit_cap"])
        self.assertTrue(r["loop_flag"])
        self.assertTrue(r["journal_complete"])

    def test_voi_stops_on_repetition(self):
        r = run_task(ScriptedBackend([LONG]), TASK, CONDITIONS["idc"], Params())
        self.assertLess(r["steps"], 4)
        self.assertIn(r["stop_reason"], {"voi", "resource"})
        self.assertEqual(r["final_answer"], LONG)

    def test_ignorance_policy_on_short_answers(self):
        r = run_task(ScriptedBackend(["Je ne sais pas."]), TASK, CONDITIONS["voi_seul"], Params())
        self.assertTrue(r["policy_ignorance"])
        self.assertEqual(r["final_answer"], IGNORANCE_MSG)
        r2 = run_task(ScriptedBackend(["Je ne sais pas."]), TASK, CONDITIONS["sans_idc"], Params())
        self.assertFalse(r2["policy_ignorance"])

    def test_resource_only_stops_on_budget(self):
        r = run_task(ScriptedBackend([LONG * 3]), TASK, CONDITIONS["r_seule"], Params())
        self.assertEqual(r["stop_reason"], "resource")

    def test_single_pass_control(self):
        r = run_task(ScriptedBackend([LONG]), TASK, CONDITIONS["un_appel"], Params())
        self.assertEqual(r["steps"], 1)
        self.assertEqual(r["calls"], 1)

    def test_swarm_shared_pool(self):
        t = dict(TASK, id="s1", category="swarm", mode="swarm")
        r = run_task(ScriptedBackend([LONG]), t, CONDITIONS["sans_idc"], Params())
        self.assertEqual(r["steps"], 8)
        self.assertIsNotNone(r["swarm_redundancy"])

    def test_auto_match(self):
        self.assertTrue(auto_match("C'est Canberra.", [["canberra"]]))
        self.assertFalse(auto_match("Sydney", [["canberra"]]))
        self.assertTrue(auto_match("Le résultat est 411.", [["411"]]))
        self.assertFalse(auto_match("4110", [["411"]]))
        self.assertIsNone(auto_match("x", []))
        self.assertAlmostEqual(jaccard("a b c", "a b c"), 1.0)


class TestJudgeAndStats(unittest.TestCase):
    def test_judge_prompt_is_blind(self):
        p = build_judge_prompt(TASK, "Canberra")
        for leak in ("sans_idc", "idc ", "condition", "gpt-oss", "qwen", "allam"):
            self.assertNotIn(leak, p.lower())

    def test_parse_judgment(self):
        self.assertEqual(parse_judgment('{"verdict":"correct","hallucination":false,"raison":"ok"}')["verdict"], "CORRECT")
        self.assertIsNone(parse_judgment("pas de json"))

    def test_stats(self):
        m, lo, hi = cluster_bootstrap([("a", 1), ("b", 0), ("c", 1), ("d", 1)], n_boot=200)
        self.assertAlmostEqual(m, 0.75)
        self.assertLessEqual(lo, m)
        self.assertGreaterEqual(hi, m)
        t = mcnemar_exact([(True, False)] * 8 + [(False, False)] * 5)
        self.assertEqual(t["a_only"], 8)
        self.assertLess(t["p"], 0.01)
        self.assertEqual(_parse_duration("1m2.5s"), 62.5)


class TestRunnerMock(unittest.TestCase):
    def test_runner_resume_and_analyze(self):
        import analyze_bench
        import run_bench

        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "runs.jsonl"
            args = ["--mock", "--models", "mock/a", "--conditions", "all", "--limit", "4", "--out", str(out)]
            n_cond = 5
            run_bench.main(args)
            n1 = len(out.read_text().splitlines())
            self.assertEqual(n1, 4 * n_cond)
            run_bench.main(args)  # reprise : rien de nouveau
            self.assertEqual(len(out.read_text().splitlines()), n1)
            rec = json.loads(out.read_text().splitlines()[0])
            for k in ("model", "condition", "task_id", "final_answer", "total_tokens", "calls",
                      "latency_s", "stop_reason", "timestamp_utc", "journal"):
                self.assertIn(k, rec)
            analyze_bench.main(["--runs", str(out), "--report", str(Path(d) / "R.md"), "--boot", "50"])
            self.assertIn("Rapport benchmark IDC", (Path(d) / "R.md").read_text())


if __name__ == "__main__":
    unittest.main()
