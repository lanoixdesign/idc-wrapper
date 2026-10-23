#!/usr/bin/env python3
"""Essaim d'agents — Baseline vs IDC (mock, aucune clé API).

Quatre rôles spécialisés partagent **un même pool R** et un **journal
append-only commun**. Avec IDC, la règle d'arrêt (VOI) coupe la boucle
avant le ping-pong bruyant ; sans IDC, les agents se renvoient la balle
jusqu'à max_rounds.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from idc import AppendOnlyJournal, IdcRunResult, JournalEntry, MockBackend
from idc.agent import IGNORANCE_MSG
from idc.mock_backend import MockScenario

# ---------------------------------------------------------------------------
# Scénario pédagogique : synthèse d'incident support
# Ordre de tour : chercheur → critique → rédacteur → coordonnateur → …
# Gains calibrés vs coût marginal ≈ cost_per_token * 50 ≈ 40.
# ---------------------------------------------------------------------------

SWARM_INCIDENT = MockScenario(
    name="swarm_incident",
    responses=[
        # Tour 1 — utile
        "[chercheur] Faits : panne API paiement 14h–14h22 UTC+2 ; 47 tickets ; "
        "rollback v2.3.1 déjà déployé ; pas de fuite de données confirmée.",
        "[critique] Conteste la généralisation « tous les clients » : seuls les "
        "paiements CB 3-D Secure étaient impactés. Demande de borner le périmètre.",
        "[rédacteur] Brouillon client : incident ciblé CB 3DS, résolu par rollback, "
        "remboursement auto si double débit sous 48 h. Pas de fuite connue.",
        # Tour 2 — bruit / ping-pong
        "[coordonnateur] Relance l'essaim pour « enrichir » : demande une 2e passe "
        "sans fait nouveau.",
        "[chercheur] Reformulation des mêmes faits + speculative SLA inventé à 99,999 %.",
        "[critique] Debate cosmétique sur le ton ; aucun risque nouveau identifié.",
        "[rédacteur] Version longue verbeuse qui dilue l'action claire.",
        # Tour 3 — hallucination
        "[coordonnateur] Propose d'inventer un post-mortem public daté demain.",
        "[chercheur] Hallucination : faux CVE-2026-99999 et faux lien status page.",
        "[critique] Contredit le faux CVE puis invente une autre cause root.",
        "[rédacteur] Synthèse bruitée mélangeant faits et inventions.",
        "[coordonnateur] Boucle : redistribue les mêmes tâches.",
    ],
    gains=[
        56.0,  # chercheur — faits
        48.0,  # critique — borne le périmètre
        44.0,  # rédacteur — réponse actionnable
        14.0,  # coordonnateur — relance faible valeur
        10.0,
        8.0,
        6.0,
        4.0,
        3.0,
        2.0,
        2.0,
        1.0,
    ],
)

ROLES = ("chercheur", "critique", "rédacteur", "coordonnateur")

TASK = (
    "Incident support : synthétiser une réponse client claire sur la panne "
    "API paiement de cet après-midi (périmètre, résolution, suite)."
)


@dataclass
class SwarmPool:
    """Pool partagé : une seule R + un journal commun pour tout l'essaim."""

    resource: float = 160.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    journal: AppendOnlyJournal = field(default_factory=AppendOnlyJournal)

    def still_worth_it(self, estimated_gain: float) -> bool:
        marginal_cost = self.cost_per_token * 50.0
        risk = 2.0 if self.resource < 30.0 else 1.0
        return estimated_gain > marginal_cost * risk


@dataclass
class SwarmRunner:
    """Orchestre les rôles en tours successifs sur le pool partagé."""

    backend: MockBackend
    pool: SwarmPool
    max_rounds: int = 3  # 3 * 4 rôles = 12 tours max
    use_stop_rule: bool = True
    useful_gain_floor: float = 40.0

    def run(self, task: str) -> IdcRunResult:
        current_parts: list[str] = []
        step = 0
        tokens_total = 0
        cost_total = 0.0
        stopped_early = False
        max_gain_seen = 0.0
        any_useful = False
        max_steps = self.max_rounds * len(ROLES)

        while self.pool.resource > self.pool.critical_threshold and step < max_steps:
            step += 1
            role = ROLES[(step - 1) % len(ROLES)]
            context = (
                f"Rôle actif : {role}\n"
                f"Journal partagé de l'essaim :\n{self.pool.journal.as_context()}\n\n"
                f"Tâche : {task}\n\n"
                "Produis ta contribution (concise)."
            )
            chunk = self.backend.generate(context, max_tokens=120)
            tokens_approx = max(len(chunk.split()), 1)
            chunk_display = chunk.strip() if chunk.strip() else "(vide / incertitude)"

            cost = tokens_approx * self.pool.cost_per_token
            self.pool.resource = max(0.0, self.pool.resource - cost)
            tokens_total += tokens_approx
            cost_total += cost
            estimated_gain = self.backend.gain_for_step(step, chunk)
            max_gain_seen = max(max_gain_seen, estimated_gain)
            if chunk.strip() and estimated_gain >= self.useful_gain_floor:
                any_useful = True

            self.pool.journal.append(
                JournalEntry(
                    step=step,
                    text=chunk_display,
                    resource_after=self.pool.resource,
                    tokens_approx=tokens_approx,
                    cost=cost,
                    estimated_gain=estimated_gain,
                )
            )

            if chunk.strip():
                current_parts.append(chunk.strip())

            should_stop = False
            if self.use_stop_rule:
                if (not self.pool.still_worth_it(estimated_gain)) or (
                    self.pool.resource <= self.pool.critical_threshold
                ):
                    should_stop = True
            else:
                if self.pool.resource <= self.pool.critical_threshold:
                    should_stop = True

            if should_stop:
                break

        if self.use_stop_rule and step < max_steps:
            stopped_early = True

        current = "\n".join(current_parts)
        if not current.strip():
            admitted = True
            answer = IGNORANCE_MSG
        elif (
            self.use_stop_rule
            and not any_useful
            and max_gain_seen < self.useful_gain_floor
        ):
            admitted = True
            answer = IGNORANCE_MSG
        else:
            admitted = False
            # Sous IDC : garder la synthèse utile (tours à gain élevé).
            # Sans IDC : tout le bruit accumulé.
            if self.use_stop_rule:
                useful = [
                    e.text
                    for e in self.pool.journal.entries
                    if e.estimated_gain >= self.useful_gain_floor
                ]
                answer = "\n".join(useful) if useful else current.strip()
            else:
                answer = current.strip()

        return IdcRunResult(
            answer=answer,
            steps=step,
            resource_final=self.pool.resource,
            tokens_approx_total=tokens_total,
            cost_total=cost_total,
            stopped_early=stopped_early,
            admitted_ignorance=admitted,
            journal=self.pool.journal,
            mode="idc" if self.use_stop_rule else "baseline",
        )


def run_once(use_idc: bool) -> IdcRunResult:
    backend = MockBackend(SWARM_INCIDENT)
    pool = SwarmPool(resource=160.0, critical_threshold=15.0, cost_per_token=0.8)
    runner = SwarmRunner(
        backend=backend,
        pool=pool,
        max_rounds=3,
        use_stop_rule=use_idc,
    )
    return runner.run(TASK)


def print_result(label: str, r: IdcRunResult) -> None:
    collapse = r.stopped_early or r.admitted_ignorance
    print(f"\n######## {label} ########")
    print(
        f"étapes={r.steps} | R_final={r.resource_final:.1f} | "
        f"tokens≈{r.tokens_approx_total} | coût≈{r.cost_total:.1f} | "
        f"arrêt_anticipé={r.stopped_early} | collapse/ignorance={collapse} | mode={r.mode}"
    )
    print("--- Journal partagé (essaim) ---")
    print(r.journal.as_context())
    print("--- Réponse textuelle ---")
    print(r.answer[:800])


def resolve_mode(argv: list[str] | None = None) -> str:
    """Retourne 'both' | 'idc' | 'baseline'.

    Priorité : flags CLI > env IDC=1|0 > défaut 'both' (comparable, comme 01–04).
    """
    parser = argparse.ArgumentParser(
        description="Essaim d'agents mock — comparaison Sans/Avec IDC"
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--idc",
        action="store_true",
        help="Active la règle d'arrêt IDC (VOI) sur le pool partagé",
    )
    g.add_argument(
        "--no-idc",
        action="store_true",
        help="Désactive IDC : boucle naïve jusqu'à max_rounds / R critique",
    )
    args = parser.parse_args(argv)

    if args.idc:
        return "idc"
    if args.no_idc:
        return "baseline"

    env = os.environ.get("IDC", "").strip()
    if env in ("1", "true", "True", "yes", "on"):
        return "idc"
    if env in ("0", "false", "False", "no", "off"):
        return "baseline"
    return "both"


def main(argv: list[str] | None = None) -> None:
    mode = resolve_mode(argv)
    print("=== Exemple 05 : Essaim d'agents (journal + R partagés) ===")
    print(f"Rôles : {', '.join(ROLES)}")
    print("Pool : R partagée + journal append-only commun (choix pédagogique).")
    print(f"Tâche : {TASK}")

    if mode in ("both", "baseline"):
        print_result(
            "SANS IDC (boucle naïve — les agents se renvoient la balle)",
            run_once(use_idc=False),
        )
    if mode in ("both", "idc"):
        print_result(
            "AVEC IDC (arrêt VOI sur pool partagé)",
            run_once(use_idc=True),
        )


if __name__ == "__main__":
    main()
