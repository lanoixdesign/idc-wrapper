#!/usr/bin/env python3
"""Micro-benchmark mock : Baseline (N fixes, pas de VOI) vs IDC (règle d'arrêt).

Écrit benchmarks/results/latest.json avec des nombres RÉELS mesurés sur cette machine.
Aucun appel LLM réseau. Ne pas interpréter comme perf production.
"""

from __future__ import annotations

import json
import platform
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from idc import IdcAgent, MockBackend
from idc.mock_backend import (
    CODE_ASSISTANT,
    RESEARCH_SYNTH,
    SUPPORT_CLIENT,
    UNCERTAIN,
    VERBOSE,
    MockScenario,
)

SCENARIOS: list[MockScenario] = [
    SUPPORT_CLIENT,
    CODE_ASSISTANT,
    RESEARCH_SYNTH,
    VERBOSE,
    UNCERTAIN,
]

TASKS = {
    "support_client": "Client : mon colis n'est pas arrivé, que faire ?",
    "code_assistant": "Corrige IndexError sur liste vide.",
    "research_synth": "Synthétise finitude et arrêt optimal.",
    "verbose": "Explique longuement un sujet simple.",
    "uncertain": "Quelle est la réponse exacte sans aucune source ?",
}


@dataclass
class Row:
    scenario: str
    mode: str
    steps: int
    tokens_approx: int
    resource_final: float
    cost_total: float
    stopped_early: bool
    admitted_ignorance: bool
    elapsed_ms: float


def one_run(scenario: MockScenario, use_stop: bool) -> Row:
    b = MockBackend(scenario)
    agent = IdcAgent(
        backend=b,
        resource=100.0,
        critical_threshold=15.0,
        cost_per_token=0.8,
        max_steps=8,
        use_stop_rule=use_stop,
        gain_fn=b.gain_for_step,
    )
    t0 = time.perf_counter()
    r = agent.run(TASKS[scenario.name])
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return Row(
        scenario=scenario.name,
        mode="idc" if use_stop else "baseline",
        steps=r.steps,
        tokens_approx=r.tokens_approx_total,
        resource_final=round(r.resource_final, 2),
        cost_total=round(r.cost_total, 2),
        stopped_early=r.stopped_early,
        admitted_ignorance=r.admitted_ignorance,
        elapsed_ms=round(elapsed_ms, 3),
    )


def main() -> None:
    rows: list[Row] = []
    for sc in SCENARIOS:
        rows.append(one_run(sc, use_stop=False))
        rows.append(one_run(sc, use_stop=True))

    # Agrégats
    def avg(mode: str, field: str) -> float:
        subset = [r for r in rows if r.mode == mode]
        return sum(getattr(r, field) for r in subset) / len(subset)

    ignorance_idc = sum(1 for r in rows if r.mode == "idc" and r.scenario == "uncertain" and r.admitted_ignorance)
    ignorance_base = sum(1 for r in rows if r.mode == "baseline" and r.scenario == "uncertain" and r.admitted_ignorance)
    # Taux sur le scénario uncertain uniquement (1 run chacun) + note
    uncertain_runs_idc = [r for r in rows if r.mode == "idc" and r.scenario == "uncertain"]
    uncertain_runs_base = [r for r in rows if r.mode == "baseline" and r.scenario == "uncertain"]

    # Multi-seed micro-runs for ignorance rate under uncertainty (deterministic mock → 0 or 1)
    # Variante : on rejoue uncertain avec budgets différents pour un taux non trivial
    ign_idc = 0
    ign_base = 0
    n_unc = 0
    for resource, thr, cpt in [(40.0, 20.0, 2.0), (50.0, 15.0, 1.5), (30.0, 15.0, 2.5), (100.0, 15.0, 0.8), (60.0, 25.0, 1.2)]:
        n_unc += 1
        for use_stop, counter_name in ((True, "idc"), (False, "base")):
            b = MockBackend(UNCERTAIN)
            agent = IdcAgent(
                backend=b,
                resource=resource,
                critical_threshold=thr,
                cost_per_token=cpt,
                max_steps=8,
                use_stop_rule=use_stop,
                gain_fn=b.gain_for_step,
            )
            rr = agent.run(TASKS["uncertain"])
            if rr.admitted_ignorance:
                if use_stop:
                    ign_idc += 1
                else:
                    ign_base += 1

    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "note": (
                "Mock LLM only. Numbers are reproducible on this machine with "
                "benchmarks/bench_mock.py. NOT production FLOPS or survival rates."
            ),
            "idc_version": "0.2.0",
        },
        "rows": [asdict(r) for r in rows],
        "aggregates": {
            "avg_steps_baseline": round(avg("baseline", "steps"), 3),
            "avg_steps_idc": round(avg("idc", "steps"), 3),
            "avg_tokens_baseline": round(avg("baseline", "tokens_approx"), 3),
            "avg_tokens_idc": round(avg("idc", "tokens_approx"), 3),
            "avg_resource_final_baseline": round(avg("baseline", "resource_final"), 3),
            "avg_resource_final_idc": round(avg("idc", "resource_final"), 3),
            "forced_ignorance_rate_uncertain_idc": round(ign_idc / n_unc, 3),
            "forced_ignorance_rate_uncertain_baseline": round(ign_base / n_unc, 3),
            "uncertain_budget_variants": n_unc,
            "single_run_uncertain_admitted_idc": bool(uncertain_runs_idc and uncertain_runs_idc[0].admitted_ignorance),
            "single_run_uncertain_admitted_baseline": bool(uncertain_runs_base and uncertain_runs_base[0].admitted_ignorance),
        },
    }

    out = Path(__file__).resolve().parent / "results" / "latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload["aggregates"], indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
