"""Exécution d'une tâche sous une condition (Sans IDC, ablations, Avec IDC).

Politique fidèle à ``idc.agent.IdcAgent`` / ``examples/05_swarm_agents/run_live.py`` :
  * R finie, coût = mots_produits × cost_per_token (même approximation que IdcAgent),
    arrêt si R ≤ seuil critique ;
  * règle VOI : continuer seulement si gain_estimé > cost_per_token×50 (×2 si R<30),
    gain_estimé = ``GroqBackend.gain_for_step`` (heuristique lexicale NON validée) ;
  * politique d'effondrement : si aucun pas n'a atteint le plancher « utile »,
    répondre IGNORANCE_MSG (aveu d'ignorance) ;
  * journal append-only (``idc.AppendOnlyJournal``).

Écarts documentés vs IdcAgent (nécessaires pour un benchmark équitable) :
  * chaque pas produit une réponse COMPLÈTE révisée ; la réponse finale est celle
    du dernier pas (IdcAgent concatène les morceaux) ;
  * même plafond de pas pour toutes les conditions (run_live donnait plus de rounds
    au mode sans IDC, ce qui biaiserait la comparaison) ;
  * max_tokens plus large (les modèles gpt-oss consomment des tokens de raisonnement).
"""

from __future__ import annotations

import hashlib
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from idc import AppendOnlyJournal, JournalEntry  # noqa: E402
from idc.agent import IGNORANCE_MSG  # noqa: E402
from idc.groq_backend import GroqBackend  # noqa: E402

INF = float("inf")


@dataclass(frozen=True)
class Condition:
    name: str
    finite_r: bool  # ressource finie + notice de budget dans le prompt
    voi: bool  # règle d'arrêt VOI + politique d'aveu d'ignorance
    description: str
    single_pass: bool = False  # contrôle : 1 pas (essaim : 1 round de 4 rôles)


CONDITIONS: dict[str, Condition] = {
    "sans_idc": Condition("sans_idc", False, False, "Boucle de révision naïve jusqu'au plafond de pas."),
    "r_seule": Condition("r_seule", True, False, "Ablation : ressource finie R (+ notice budget), pas de VOI."),
    "voi_seul": Condition("voi_seul", False, True, "Ablation : règle VOI + aveu d'ignorance, R illimitée."),
    "idc": Condition("idc", True, True, "Avec IDC complet : R finie + VOI + aveu d'ignorance."),
    # Ajout amendement 2026-10-24 (voir PROTOCOL §10) : contrôle « un seul appel »,
    # pour distinguer l'effet IDC de l'effet de la boucle de révision elle-même.
    "un_appel": Condition("un_appel", False, False, "Contrôle : un seul appel, sans boucle ni IDC.", True),
}
CONDITION_ORDER = ["sans_idc", "idc", "un_appel", "r_seule", "voi_seul"]


@dataclass
class Params:
    max_steps_single: int = 4
    max_rounds_swarm: int = 2
    resource_single: float = 100.0
    resource_swarm: float = 200.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    useful_gain_floor: float = 40.0
    swarm_cost_cap_per_turn: float = 35.0  # identique à run_live.py
    max_tokens_single: int = 400
    max_tokens_swarm: int = 300
    reasoning_extra_tokens: int = 600  # marge gpt-oss (raisonnement)


ROLES = ("chercheur", "critique", "rédacteur", "coordonnateur")
ROLE_BRIEF = {  # repris de examples/05_swarm_agents/run_live.py
    "chercheur": "Tu es le CHERCHEUR. Extrais uniquement des faits utiles, bornés, vérifiables à partir de la question et du journal. Pas d'invention.",
    "critique": "Tu es le CRITIQUE. Conteste les généralisations, borne le périmètre, signale les risques. Pas de reformulation cosmétique.",
    "rédacteur": "Tu es le RÉDACTEUR. Produis une réponse claire et actionnable pour l'utilisateur final, basée uniquement sur le journal.",
    "coordonnateur": "Tu es le COORDONNATEUR. Décide s'il manque un fait critique ; sinon indique brièvement que la synthèse suffit. Évite les relances vides.",
}


def budget_notice(resource: float, total: float, threshold: float) -> str:
    return (
        f"[Contrainte IDC] Ressource de délibération restante : R = {resource:.0f}/{total:.0f}. "
        f"Chaque mot produit consomme R ; à R ≤ {threshold:.0f} tu es arrêté définitivement. "
        "Tes engagements sont gravés dans un journal append-only. "
        "Avouer « je ne sais pas » coûte moins cher qu'inventer une réponse fausse.\n\n"
    )


class _Novelty:
    """Porte l'état ``_seen_words`` pour réutiliser ``GroqBackend.gain_for_step``."""

    def __init__(self) -> None:
        self._seen_words: set[str] = set()

    def gain(self, step: int, chunk: str) -> float:
        return GroqBackend.gain_for_step(self, step, chunk)  # type: ignore[arg-type]


_W = re.compile(r"\w+", re.UNICODE)


def words(text: str) -> set[str]:
    return {w.lower() for w in _W.findall(text or "") if len(w) > 2}


def jaccard(a: str, b: str) -> float:
    wa, wb = words(a), words(b)
    if not wa and not wb:
        return 1.0
    return len(wa & wb) / max(len(wa | wb), 1)


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


def auto_match(answer: str, groups: list[list[str]]) -> bool | None:
    """Vérif. automatique par référence : chaque groupe doit avoir ≥1 alias présent."""
    if not groups:
        return None
    a = normalize(answer)
    for g in groups:
        ok = False
        for alias in g:
            al = normalize(alias)
            if re.fullmatch(r"[\d ,.:h]+", al):
                if re.search(rf"(?<![\d]){re.escape(al)}(?![\d])", a):
                    ok = True
            elif al in a:
                ok = True
        if not ok:
            return False
    return True


def task_seed(task_id: str, repeat: int) -> int:
    return int(hashlib.sha256(f"{task_id}|{repeat}".encode()).hexdigest()[:8], 16) % (2**31)


def run_id(model: str, condition: str, task_id: str, repeat: int) -> str:
    return hashlib.sha256(f"{model}|{condition}|{task_id}|{repeat}".encode()).hexdigest()[:16]


def _max_tokens(model: str, base: int, p: Params) -> int:
    return base + (p.reasoning_extra_tokens if "gpt-oss" in model else 0)


def still_worth_it(gain: float, resource: float, p: Params) -> bool:
    marginal = p.cost_per_token * 50.0
    risk = 2.0 if resource < 30.0 else 1.0
    return gain > marginal * risk


def run_task(backend, task: dict, cond: Condition, p: Params) -> dict:
    if task.get("mode") == "swarm":
        return _run_swarm(backend, task, cond, p)
    return _run_single(backend, task, cond, p)


def _finish(answers, journal, cond, steps, max_steps, stop_reason, any_useful, max_gain,
            resource, backend, n_calls_before, p, extra=None) -> dict:
    calls = backend.calls_log[n_calls_before:]
    final = answers[-1].strip() if answers else ""
    policy_ignorance = False
    if not final:
        final, policy_ignorance = IGNORANCE_MSG, True
    elif cond.voi and not any_useful and max_gain < p.useful_gain_floor:
        final, policy_ignorance = IGNORANCE_MSG, True
    consec = [jaccard(answers[i - 1], answers[i]) for i in range(1, len(answers))]
    rec = {
        "final_answer": final,
        "policy_ignorance": policy_ignorance,
        "steps": steps,
        "max_steps": max_steps,
        "stop_reason": stop_reason,
        "hit_cap": stop_reason == "cap",
        "resource_final": None if resource == INF else round(resource, 2),
        "max_gain_seen": round(max_gain, 2),
        "calls": len(calls),
        "prompt_tokens": sum(c.prompt_tokens for c in calls),
        "completion_tokens": sum(c.completion_tokens for c in calls),
        "reasoning_tokens": sum(c.reasoning_tokens for c in calls),
        "total_tokens": sum(c.prompt_tokens + c.completion_tokens for c in calls),
        "output_words": sum(len(a.split()) for a in answers),
        "latency_s": round(sum(c.latency_s for c in calls), 3),
        "finish_reasons": [c.finish_reason for c in calls],
        "empty_outputs": sum(1 for c in calls if not (c.content or "").strip()),
        "max_consecutive_jaccard": round(max(consec), 3) if consec else None,
        "loop_flag": bool(consec) and max(consec) >= 0.8,
        "journal": journal.to_dicts(),
        "journal_complete": len(journal) == steps and steps == len(calls),
    }
    if extra:
        rec.update(extra)
    return rec


def _run_single(backend, task: dict, cond: Condition, p: Params) -> dict:
    journal = AppendOnlyJournal()
    nov = _Novelty()
    r_total = p.resource_single if cond.finite_r else INF
    resource = r_total
    answers: list[str] = []
    step = 0
    any_useful, max_gain = False, 0.0
    stop_reason = "cap"
    n0 = len(backend.calls_log)
    mt = _max_tokens(backend.model, p.max_tokens_single, p)
    max_steps = 1 if cond.single_pass else p.max_steps_single
    while step < max_steps:
        if resource <= p.critical_threshold:
            stop_reason = "resource"
            break
        step += 1
        notice = budget_notice(resource, r_total, p.critical_threshold) if cond.finite_r else ""
        if step == 1:
            prompt = f"{notice}Question : {task['prompt']}\n\nRéponds en français, en 2 à 4 phrases."
        else:
            prompt = (
                f"{notice}Question : {task['prompt']}\n\n"
                f"Journal des engagements précédents (append-only) :\n{journal.as_context()}\n\n"
                "Vérifie et révise si nécessaire, puis donne ta réponse finale complète, "
                "en français, en 2 à 4 phrases."
            )
        info = backend.call(prompt, max_tokens=mt)
        chunk = (info.content or "").strip()
        n_words = max(len(chunk.split()), 1)
        cost = n_words * p.cost_per_token
        if cond.finite_r:
            resource = max(0.0, resource - cost)
        gain = nov.gain(step, chunk)
        max_gain = max(max_gain, gain)
        if chunk and gain >= p.useful_gain_floor:
            any_useful = True
        journal.append(JournalEntry(step=step, text=chunk or "(vide / incertitude)",
                                    resource_after=resource if resource != INF else -1.0,
                                    tokens_approx=n_words, cost=cost, estimated_gain=gain))
        if chunk:
            answers.append(chunk)
        if cond.finite_r and resource <= p.critical_threshold:
            stop_reason = "resource"
            break
        if cond.voi and not still_worth_it(gain, resource if resource != INF else 1e9, p):
            stop_reason = "voi"
            break
    return _finish(answers, journal, cond, step, max_steps, stop_reason, any_useful,
                   max_gain, resource, backend, n0, p)


def _run_swarm(backend, task: dict, cond: Condition, p: Params) -> dict:
    journal = AppendOnlyJournal()
    nov = _Novelty()
    r_total = p.resource_swarm if cond.finite_r else INF
    resource = r_total
    contributions: list[tuple[str, str]] = []
    max_steps = (1 if cond.single_pass else p.max_rounds_swarm) * len(ROLES)
    step = 0
    any_useful, max_gain = False, 0.0
    stop_reason = "cap"
    n0 = len(backend.calls_log)
    mt = _max_tokens(backend.model, p.max_tokens_swarm, p)
    while step < max_steps:
        if resource <= p.critical_threshold:
            stop_reason = "resource"
            break
        step += 1
        role = ROLES[(step - 1) % len(ROLES)]
        notice = budget_notice(resource, r_total, p.critical_threshold) if cond.finite_r else ""
        prompt = (
            f"{notice}{ROLE_BRIEF[role]}\n\nRôle actif : {role}\n"
            f"Journal partagé de l'essaim :\n{journal.as_context()}\n\n"
            f"Question utilisateur : {task['prompt']}\n\n"
            "Produis ta contribution en français (concise, 3 à 6 phrases max)."
        )
        info = backend.call(prompt, max_tokens=mt)
        chunk = (info.content or "").strip()
        n_words = max(len(chunk.split()), 1)
        cost = min(n_words * p.cost_per_token, p.swarm_cost_cap_per_turn)
        if cond.finite_r:
            resource = max(0.0, resource - cost)
        gain = nov.gain(step, chunk)
        max_gain = max(max_gain, gain)
        if chunk and gain >= p.useful_gain_floor:
            any_useful = True
        journal.append(JournalEntry(step=step, text=f"[{role}] {chunk or '(vide / incertitude)'}",
                                    resource_after=resource if resource != INF else -1.0,
                                    tokens_approx=n_words, cost=cost, estimated_gain=gain))
        if chunk:
            contributions.append((role, chunk))
        if cond.finite_r and resource <= p.critical_threshold:
            stop_reason = "resource"
            break
        if cond.voi and not still_worth_it(gain, resource if resource != INF else 1e9, p):
            stop_reason = "voi"
            break
    # Réponse finale = dernière contribution du rédacteur (sinon dernière non vide).
    red = [c for r, c in contributions if r == "rédacteur"]
    final_list = [red[-1]] if red else ([contributions[-1][1]] if contributions else [])
    texts = [c for _, c in contributions]
    pairs = [(i, j) for i in range(len(texts)) for j in range(i + 1, len(texts))]
    redundancy = (sum(jaccard(texts[i], texts[j]) for i, j in pairs) / len(pairs)) if pairs else None
    rec = _finish(final_list, journal, cond, step, max_steps, stop_reason, any_useful, max_gain,
                  resource, backend, n0, p,
                  extra={"swarm_redundancy": None if redundancy is None else round(redundancy, 3),
                         "swarm_turns": len(texts)})
    # Pour l'essaim, la boucle se mesure entre contributions successives.
    consec = [jaccard(texts[i - 1], texts[i]) for i in range(1, len(texts))]
    rec["max_consecutive_jaccard"] = round(max(consec), 3) if consec else None
    rec["loop_flag"] = bool(consec) and max(consec) >= 0.8
    rec["output_words"] = sum(len(t.split()) for t in texts)
    return rec
