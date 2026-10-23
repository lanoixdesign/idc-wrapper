#!/usr/bin/env python3
"""Essaim d'agents — Mode live Groq (vraie question, Sans/Avec IDC).

Requiert ``GROQ_API_KEY``. Conserve ``run_mock.py`` intact pour la CI.

Heuristique VOI : voir ``idc.groq_backend.GroqBackend.gain_for_step``
(décroissance par round + nouveauté lexicale). Ce n'est **pas** une preuve
empirique de gains IDC en production.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from idc import AppendOnlyJournal, IdcRunResult, JournalEntry
from idc.agent import IGNORANCE_MSG
from idc.groq_backend import DEFAULT_GROQ_MODEL, GroqBackend

ROLES = ("chercheur", "critique", "rédacteur", "coordonnateur")

ROLE_BRIEF = {
    "chercheur": (
        "Tu es le CHERCHEUR. Extrais uniquement des faits utiles, bornés, "
        "vérifiables à partir de la question et du journal. Pas d'invention."
    ),
    "critique": (
        "Tu es le CRITIQUE. Conteste les généralisations, borne le périmètre, "
        "signale les risques. Pas de reformulation cosmétique."
    ),
    "rédacteur": (
        "Tu es le RÉDACTEUR. Produis une réponse claire et actionnable pour "
        "l'utilisateur final, basée uniquement sur le journal."
    ),
    "coordonnateur": (
        "Tu es le COORDONNATEUR. Décide s'il manque un fait critique ; sinon "
        "indique brièvement que la synthèse suffit. Évite les relances vides."
    ),
}


@dataclass
class SwarmPool:
    """Pool partagé : une seule R + un journal commun pour tout l'essaim."""

    resource: float = 200.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    journal: AppendOnlyJournal = field(default_factory=AppendOnlyJournal)

    def still_worth_it(self, estimated_gain: float) -> bool:
        marginal_cost = self.cost_per_token * 50.0
        risk = 2.0 if self.resource < 30.0 else 1.0
        return estimated_gain > marginal_cost * risk


@dataclass
class SwarmRunner:
    """Orchestre les rôles en tours successifs sur le pool partagé (live)."""

    backend: GroqBackend
    pool: SwarmPool
    max_rounds: int = 3
    use_stop_rule: bool = True
    useful_gain_floor: float = 40.0
    max_tokens_per_turn: int = 180

    def run(self, question: str) -> IdcRunResult:
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
                f"{ROLE_BRIEF[role]}\n\n"
                f"Rôle actif : {role}\n"
                f"Journal partagé de l'essaim :\n{self.pool.journal.as_context()}\n\n"
                f"Question utilisateur : {question}\n\n"
                "Produis ta contribution (concise, 3–6 phrases max)."
            )
            chunk = self.backend.generate(context, max_tokens=self.max_tokens_per_turn)
            # Préférer les tokens API si dispo, sinon approx mots.
            usage = self.backend.last_usage or {}
            api_tok = int(usage.get("completion_tokens") or 0) + int(
                usage.get("prompt_tokens") or 0
            )
            tokens_approx = api_tok if api_tok > 0 else max(len(chunk.split()), 1)
            chunk_display = chunk.strip() if chunk.strip() else "(vide / incertitude)"

            cost = tokens_approx * self.pool.cost_per_token
            # Pour live, le coût pédagogique ne doit pas vider R trop vite
            # sur de gros prompts : plafonner le prélèvement par tour.
            cost = min(cost, 35.0)
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
                    text=f"[{role}] {chunk_display}",
                    resource_after=self.pool.resource,
                    tokens_approx=tokens_approx,
                    cost=cost,
                    estimated_gain=estimated_gain,
                )
            )

            if chunk.strip():
                current_parts.append(f"[{role}] {chunk.strip()}")

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


def run_once(
    question: str,
    *,
    use_idc: bool,
    model: str,
    max_rounds_idc: int,
    max_rounds_baseline: int,
) -> tuple[IdcRunResult, dict[str, int]]:
    backend = GroqBackend.from_env(model=model)
    pool = SwarmPool(resource=200.0, critical_threshold=15.0, cost_per_token=0.8)
    rounds = max_rounds_idc if use_idc else max_rounds_baseline
    runner = SwarmRunner(
        backend=backend,
        pool=pool,
        max_rounds=rounds,
        use_stop_rule=use_idc,
    )
    result = runner.run(question)
    return result, backend.usage_summary()


def print_result(label: str, r: IdcRunResult, usage: dict[str, int]) -> None:
    collapse = r.stopped_early or r.admitted_ignorance
    print(f"\n######## {label} ########")
    print(
        f"étapes={r.steps} | R_final={r.resource_final:.1f} | "
        f"tokens≈{r.tokens_approx_total} | coût_pédagogique≈{r.cost_total:.1f} | "
        f"arrêt_anticipé={r.stopped_early} | collapse/ignorance={collapse} | mode={r.mode}"
    )
    print(
        f"usage Groq API : calls={usage.get('calls', 0)} | "
        f"prompt_tokens={usage.get('prompt_tokens', 0)} | "
        f"completion_tokens={usage.get('completion_tokens', 0)} | "
        f"total_tokens={usage.get('total_tokens', 0)}"
    )
    print("--- Journal partagé (essaim) ---")
    print(r.journal.as_context())
    print("--- Réponse textuelle ---")
    print(r.answer[:2000])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Essaim d'agents live Groq — comparaison Sans/Avec IDC"
    )
    p.add_argument(
        "--question",
        "-q",
        required=True,
        help="Question / tâche posée à l'essaim (obligatoire)",
    )
    g = p.add_mutually_exclusive_group()
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
    p.add_argument(
        "--model",
        default=os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL),
        help=f"Modèle Groq (défaut : {DEFAULT_GROQ_MODEL})",
    )
    p.add_argument(
        "--max-rounds-idc",
        type=int,
        default=3,
        help="Rounds max avec IDC (défaut 3 → 12 tours max, souvent stop VOI avant)",
    )
    p.add_argument(
        "--max-rounds-baseline",
        type=int,
        default=5,
        help="Rounds max sans IDC (défaut 5 → plus haut que le mode IDC)",
    )
    return p


def resolve_mode(args: argparse.Namespace) -> str:
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
    parser = build_parser()
    args = parser.parse_args(argv)
    mode = resolve_mode(args)
    question = args.question.strip()
    if not question:
        raise SystemExit("--question ne peut pas être vide")
    # Échoue tôt si la clé manque (évite un bandeau inutile).
    if not os.environ.get("GROQ_API_KEY", "").strip():
        raise SystemExit(
            "GROQ_API_KEY manquante. Exportez la clé Groq "
            "(https://console.groq.com/keys) puis relancez."
        )

    print("=== Exemple 05 : Essaim d'agents LIVE (Groq) ===")
    print(f"Rôles : {', '.join(ROLES)}")
    print(f"Modèle : {args.model}")
    print("Pool : R partagée + journal append-only commun.")
    print(
        "Gain VOI : heuristique (base décroissante × nouveauté lexicale) — "
        "voir idc.groq_backend ; pas un claim empirique."
    )
    print(f"Question : {question}")

    if mode in ("both", "baseline"):
        r, usage = run_once(
            question,
            use_idc=False,
            model=args.model,
            max_rounds_idc=args.max_rounds_idc,
            max_rounds_baseline=args.max_rounds_baseline,
        )
        print_result(
            "SANS IDC (boucle naïve — max_rounds plus haut, pas de stop VOI)",
            r,
            usage,
        )
    if mode in ("both", "idc"):
        r, usage = run_once(
            question,
            use_idc=True,
            model=args.model,
            max_rounds_idc=args.max_rounds_idc,
            max_rounds_baseline=args.max_rounds_baseline,
        )
        print_result(
            "AVEC IDC (arrêt VOI sur pool partagé)",
            r,
            usage,
        )


if __name__ == "__main__":
    main()
