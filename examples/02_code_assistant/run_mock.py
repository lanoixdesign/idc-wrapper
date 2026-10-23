#!/usr/bin/env python3
"""Comparaison Baseline vs IDC — assistant code (mock)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from idc import IdcAgent, MockBackend
from idc.mock_backend import CODE_ASSISTANT


def run(label: str, use_stop: bool) -> None:
    b = MockBackend(CODE_ASSISTANT)
    agent = IdcAgent(
        backend=b,
        resource=100.0,
        critical_threshold=15.0,
        cost_per_token=0.8,
        max_steps=8,
        use_stop_rule=use_stop,
        gain_fn=b.gain_for_step,
    )
    task = "Corrige IndexError sur liste vide dans get_first(items)."
    r = agent.run(task)
    print(f"\n######## {label} ########")
    print(f"étapes={r.steps} | R_final={r.resource_final:.1f} | "
          f"tokens≈{r.tokens_approx_total} | arrêt_anticipé={r.stopped_early}")
    print("--- Journal ---")
    print(r.journal.as_context())
    print("--- Réponse ---")
    print(r.answer[:500])


if __name__ == "__main__":
    print("=== Exemple 02 : Assistant code ===")
    run("BASELINE (fixe max_steps, pas de VOI)", use_stop=False)
    run("IDC (règle d'arrêt)", use_stop=True)
