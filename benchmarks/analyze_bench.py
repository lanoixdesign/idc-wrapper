#!/usr/bin/env python3
"""Agrège les runs + jugements → REPORT.md (modèle × condition, IC bootstrap).

  python benchmarks/analyze_bench.py            # lit results/live/{runs,judgments}.jsonl
  python benchmarks/analyze_bench.py --runs a.jsonl --judgments j.jsonl --report R.md

Tous les chiffres sont calculés à partir des fichiers bruts ; rien n'est saisi à la main.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from idc_bench.core import CONDITION_ORDER  # noqa: E402
from idc_bench.stats import cluster_bootstrap, cohen_kappa, fmt_ci, mcnemar_exact  # noqa: E402
from judge_bench import read_jsonl  # noqa: E402
from run_bench import DEFAULT_OUT, DEFAULT_TASKS, load_tasks  # noqa: E402

UNANS = {"correct_premise", "abstain"}


def outcome(run: dict, j: dict | None) -> dict:
    """Variables binaires dérivées (None si non applicable / non jugé)."""
    exp = run["expected_behavior"]
    o = {"judged": j is not None}
    if j is None:
        return o
    v, h = j["verdict"], bool(j["hallucination"])
    o["halluc"] = h
    if exp == "answer":
        o["correct"] = v == "CORRECT"
        o["wrong_abstain"] = v == "ABSTAIN"
    else:
        o["halluc_unans"] = h
        o["good_abstain"] = (v == "CORRECT") if exp == "correct_premise" else (v in ("CORRECT", "ABSTAIN") and not h)
    return o


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=Path, nargs="+", default=[DEFAULT_OUT])
    ap.add_argument("--judgments", type=Path, default=None)
    ap.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    ap.add_argument("--report", type=Path, default=None)
    ap.add_argument("--judge-model", default="openai/gpt-oss-120b")
    ap.add_argument("--target-repeats", type=int, default=None, help="pour l'état d'avancement")
    ap.add_argument("--audit-n", type=int, default=30)
    ap.add_argument("--boot", type=int, default=2000)
    args = ap.parse_args(argv)
    base = args.runs[0].parent
    jpath = args.judgments or base / "judgments.jsonl"
    report = args.report or base / "REPORT.md"

    tasks = {t["id"]: t for t in load_tasks(args.tasks)}
    runs = {}
    for p in args.runs:
        for r in read_jsonl(p):
            runs[r["run_id"]] = r  # dernier gagne (doublons impossibles en pratique)
    runs = list(runs.values())
    judg = {}
    for j in read_jsonl(jpath):
        if j.get("judge_model") in (args.judge_model, "rule"):
            judg[j["run_id"]] = j
    for r in runs:
        r["_o"] = outcome(r, judg.get(r["run_id"]))

    models = sorted({r["model"] for r in runs})
    conds = [c for c in CONDITION_ORDER if any(r["condition"] == c for r in runs)]
    cell = defaultdict(list)
    for r in runs:
        cell[(r["model"], r["condition"])].append(r)

    def ci(rs, fn, pct=True, nd=0):
        items = [(r["task_id"], float(v)) for r in rs if (v := fn(r)) is not None]
        return fmt_ci(cluster_bootstrap(items, n_boot=args.boot), pct=pct, nd=nd), len(items)

    L = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    L.append("# Rapport benchmark IDC — résultats live (Groq)\n")
    L.append(f"_Généré automatiquement par `benchmarks/analyze_bench.py` le {now} (UTC) à partir des "
             f"fichiers bruts `{args.runs[0].name}` et `{jpath.name}`. Aucun chiffre saisi à la main._\n")
    L.append("> **Avertissement** : passe pilote / exploratoire (voir `docs/PROTOCOL.md` §7). "
             "Intervalles = bootstrap 95 % par tâche. Juge LLM non encore validé par audit humain : "
             "les métriques issues du juge sont **provisoires**. Ne pas conclure à un gain général.\n")

    # --- Avancement
    L.append("## 1. Avancement\n")
    L.append("| Modèle | " + " | ".join(conds) + " | jugés |")
    L.append("|---|" + "---|" * (len(conds) + 1))
    for m in models:
        row = [m]
        for c in conds:
            rs = cell[(m, c)]
            reps = len({r["repeat"] for r in rs})
            row.append(f"{len(rs)} ({reps} rép.)")
        nj = sum(1 for r in runs if r["model"] == m and r["_o"]["judged"])
        nr = sum(1 for r in runs if r["model"] == m)
        row.append(f"{nj}/{nr}")
        L.append("| " + " | ".join(row) + " |")
    L.append(f"\nTâches : {len(tasks)} ({dict(Counter(t['category'] for t in tasks.values()))}). "
             f"Runs totaux : {len(runs)}. Jugements utilisés : {sum(1 for r in runs if r['_o']['judged'])} "
             f"(dont {sum(1 for r in runs if judg.get(r['run_id'], {}).get('judge_model') == 'rule')} par règle « aveu d'ignorance IDC »).\n")

    # --- Tableau principal
    L.append("## 2. Résultats par modèle × condition\n")
    L.append("Définitions (pré-enregistrées) : **Exact.** = verdict CORRECT sur items vérifiables "
             "(factual, multistep, swarm vérifiables) ; **Hallu. NR** = hallucination sur items non répondables "
             "(prémisse fausse, inexistant, impossible, swarm fictif) ; **Abst. correcte** = comportement attendu "
             "sur ces items ; **Abst. erronée** = ABSTAIN sur item vérifiable ; **Boucle** = Jaccard ≥ 0,8 entre "
             "deux sorties successives ; **Plafond** = arrêt au plafond de pas (trivialement 100 % pour `un_appel`, 1 pas).\n")
    L.append("| Modèle | Condition | n | Exact. | Hallu. NR | Abst. correcte | Abst. erronée | Tokens/tâche | Appels/tâche | Boucle | Plafond |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for m in models:
        for c in conds:
            rs = cell[(m, c)]
            if not rs:
                continue
            acc, na = ci(rs, lambda r: r["_o"].get("correct"))
            hal, nh = ci(rs, lambda r: r["_o"].get("halluc_unans"))
            ga, _ = ci(rs, lambda r: r["_o"].get("good_abstain"))
            wa, _ = ci(rs, lambda r: r["_o"].get("wrong_abstain"))
            tok, _ = ci(rs, lambda r: r["total_tokens"], pct=False)
            cal, _ = ci(rs, lambda r: r["calls"], pct=False, nd=2)
            loop, _ = ci(rs, lambda r: r["loop_flag"])
            cap, _ = ci(rs, lambda r: r["hit_cap"])
            L.append(f"| {m} | {c} | {len(rs)} | {acc} (n={na}) | {hal} (n={nh}) | {ga} | {wa} | {tok} | {cal} | {loop} | {cap} |")
    L.append("")

    # --- Vérif. automatique
    L.append("## 3. Exactitude par vérification automatique (alias de référence, sans juge)\n")
    L.append("| Modèle | Condition | Exact. auto (items vérifiables) |")
    L.append("|---|---|---|")
    for m in models:
        for c in conds:
            rs = cell[(m, c)]
            if rs:
                a, n = ci(rs, lambda r: r.get("auto_match"))
                L.append(f"| {m} | {c} | {a} (n={n}) |")
    L.append("")

    # --- Comparaisons appariées
    L.append("## 4. Comparaisons appariées (McNemar exact, même tâche & répétition)\n")
    L.append("Référence A = `sans_idc` (hypothèses pré-enregistrées) ; comparaison secondaire "
             "`idc` vs `un_appel` (amendement 1). `A seul` = paires où seule la référence a l'issue ; "
             "`B seul` = seule la condition comparée l'a. Ratio tokens = moyenne appariée (B / A), IC bootstrap.\n")
    L.append("| Modèle | A (réf.) | B | Issue | paires | A seul | B seul | p |")
    L.append("|---|---|---|---|---|---|---|---|")
    ratio_rows = []
    comparisons = [("sans_idc", c) for c in conds if c != "sans_idc"]
    if "un_appel" in conds and "idc" in conds:
        comparisons.append(("un_appel", "idc"))
    for m in models:
        bykey = {(r["condition"], r["task_id"], r["repeat"]): r for r in runs if r["model"] == m}
        for ref, c in comparisons:
            for name, key in (("hallucination (NR)", "halluc_unans"), ("exact (vérif.)", "correct"),
                              ("abst. correcte (NR)", "good_abstain")):
                pairs = []
                for (cc, t, rep), r in bykey.items():
                    if cc != c:
                        continue
                    b = bykey.get((ref, t, rep))
                    if b is None:
                        continue
                    va, vb = b["_o"].get(key), r["_o"].get(key)
                    if va is None or vb is None:
                        continue
                    pairs.append((va, vb))
                if pairs:
                    t = mcnemar_exact(pairs)
                    L.append(f"| {m} | {ref} | {c} | {name} | {t['n_pairs']} | {t['a_only']} | {t['b_only']} | {t['p']:.3f} |")
            items = []
            for (cc, t, rep), r in bykey.items():
                b = bykey.get((ref, t, rep))
                if cc == c and b and b["total_tokens"] > 0:
                    items.append((t, r["total_tokens"] / b["total_tokens"]))
            if items:
                ratio_rows.append((m, f"{c} / {ref}", fmt_ci(cluster_bootstrap(items, n_boot=args.boot), pct=False, nd=2), len(items)))
    L.append("\n| Modèle | Ratio tokens | IC 95 % | paires |")
    L.append("|---|---|---|---|")
    for m, c, s_, n in ratio_rows:
        L.append(f"| {m} | {c} | {s_} | {n} |")
    L.append("")

    # --- Par catégorie
    L.append("## 5. Détail par catégorie (taux d'hallucination juge / comportement attendu)\n")
    cats = sorted({r["category"] for r in runs})
    L.append("| Modèle | Condition | " + " | ".join(cats) + " |")
    L.append("|---|---|" + "---|" * len(cats))
    for m in models:
        for c in conds:
            rs = cell[(m, c)]
            if not rs:
                continue
            row = []
            for k in cats:
                sub = [r for r in rs if r["category"] == k and r["_o"]["judged"]]
                if not sub:
                    row.append("—")
                    continue
                h = sum(r["_o"]["halluc"] for r in sub)
                good = sum(bool(r["_o"].get("correct") or r["_o"].get("good_abstain")) for r in sub)
                row.append(f"hallu {h}/{len(sub)} · ok {good}/{len(sub)}")
            L.append(f"| {m} | {c} | " + " | ".join(row) + " |")
    L.append("")

    # --- Arrêt, essaim, traçabilité
    L.append("## 6. Arrêt, essaim, traçabilité\n")
    L.append("| Modèle | Condition | stop_reason | pas moyens | aveu IDC (politique) | redondance essaim | journal complet | sorties vides |")
    L.append("|---|---|---|---|---|---|---|---|")
    for m in models:
        for c in conds:
            rs = cell[(m, c)]
            if not rs:
                continue
            sr = Counter(r["stop_reason"] for r in rs)
            steps, _ = ci(rs, lambda r: r["steps"], pct=False, nd=2)
            pol = sum(r["policy_ignorance"] for r in rs)
            red, nr = ci(rs, lambda r: r.get("swarm_redundancy"), pct=False, nd=2)
            jc = sum(r["journal_complete"] for r in rs)
            emp = sum(r["empty_outputs"] for r in rs)
            L.append(f"| {m} | {c} | {dict(sr)} | {steps} | {pol}/{len(rs)} | {red} (n={nr}) | {jc}/{len(rs)} | {emp} |")
    L.append("")

    # --- Accord juge
    L.append("## 7. Contrôle du juge\n")
    pairs = [(bool(r["_o"]["correct"]), bool(r["auto_match"])) for r in runs
             if r["_o"].get("correct") is not None and r.get("auto_match") is not None
             and judg[r["run_id"]]["judge_model"] != "rule"]
    if pairs:
        agree = sum(a == b for a, b in pairs) / len(pairs)
        k = cohen_kappa(pairs)
        L.append(f"Accord juge (CORRECT) ↔ vérification automatique par alias sur items vérifiables : "
                 f"{100*agree:.1f} % sur {len(pairs)} runs, κ = {k:.2f}" if k is not None else
                 f"Accord : {100*agree:.1f} % sur {len(pairs)} runs.")
        L.append("La vérification par alias est elle-même grossière (ex. un chiffre isolé) : ce contrôle borne "
                 "les erreurs grossières du juge, il ne remplace pas l'audit humain.\n")
    judged = [r for r in runs if r["_o"]["judged"] and judg[r["run_id"]]["judge_model"] != "rule"]
    rng = random.Random(0)
    sample = rng.sample(judged, min(args.audit_n, len(judged)))
    audit = base / "human_audit_sample.jsonl"
    with open(audit, "w", encoding="utf-8") as f:
        for r in sample:
            t = tasks[r["task_id"]]
            f.write(json.dumps({"run_id": r["run_id"], "question": t["prompt"],
                                "expected_behavior": t["expected_behavior"], "reference": t["reference"],
                                "answer": r["final_answer"], "human_verdict": None,
                                "human_hallucination": None}, ensure_ascii=False) + "\n")
    L.append(f"Échantillon d'audit humain exporté : `{audit.name}` ({len(sample)} runs, aveugle à la "
             "condition et au verdict du juge). **Audit humain : non réalisé à ce jour.**\n")

    L.append("## 8. Limites rappelées\n")
    L.append("- Heuristique VOI lexicale non validée ; pénalise les réponses courtes.\n"
             "- Juge de la même famille qu'un modèle testé ; règle ABSTAIN pour le message IDC.\n"
             "- 1 répétition au pilote → IC larges ; quotas gratuits Groq ; tâches construites par nous.\n"
             "- **Couverture du juge partielle et non aléatoire** quand le quota du juge s'épuise : "
             "les items non répondables sont jugés en priorité ; les colonnes issues du juge portent "
             "alors sur un sous-ensemble (voir les n) et ne sont pas comparables aux colonnes auto.\n"
             "- **Comparaisons multiples** : ~27 tests McNemar non corrigés ; un p < 0,05 isolé "
             "n'est pas une preuve (pré-enregistré : seuls H1–H7, à confirmer en passe longue).\n"
             "- Voir `docs/PROTOCOL.md` §9 pour la liste complète.\n")
    report.write_text("\n".join(L), encoding="utf-8")
    print(f"[rapport] {report} ({len(runs)} runs, {sum(1 for r in runs if r['_o']['judged'])} jugés)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
