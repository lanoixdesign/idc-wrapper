#!/usr/bin/env python3
"""Exemple LangGraph-shaped — Baseline vs IDC (mock, aucune clé API).

N'installe PAS langgraph : utilise `IdcGraphRunner`, boucle nœud/état
miroir d'un StateGraph. Pour un vrai graphe LangGraph :

    pip install 'idc-wrapper[langgraph]'
    # puis compile_langgraph(...) — voir README de cet exemple.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from idc import MockBackend
from idc.langgraph_adapter import IdcGraphRunner
from idc.mock_backend import VERBOSE


def run(label: str, use_stop: bool) -> None:
    b = MockBackend(VERBOSE)
    runner = IdcGraphRunner(
        backend=b,
        resource=100.0,
        critical_threshold=15.0,
        cost_per_token=0.8,
        max_steps=8,
        use_stop_rule=use_stop,
        gain_fn=b.gain_for_step,
    )
    r = runner.run("Explique un problème verbeux puis arrête-toi au bon moment.")
    print(f"\n######## {label} ########")
    print(
        f"étapes={r.steps} | R_final={r.resource_final:.1f} | "
        f"tokens≈{r.tokens_approx_total} | arrêt_anticipé={r.stopped_early} | mode={r.mode}"
    )
    print("--- Journal ---")
    print(r.journal.as_context())
    print("--- Réponse ---")
    print(r.answer[:500])


if __name__ == "__main__":
    print("=== Exemple 04 : Adaptateur LangGraph-shaped (mock) ===")
    print("(aucune dépendance langgraph requise pour ce script)")
    run("BASELINE (boucle jusqu'à max_steps / R critique)", use_stop=False)
    run("IDC (règle d'arrêt VOI dans le nœud)", use_stop=True)
