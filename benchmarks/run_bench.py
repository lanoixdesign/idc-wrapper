#!/usr/bin/env python3
"""Runner CLI du benchmark IDC (live Groq ou mock).

Exemples :
  python benchmarks/run_bench.py --list-models
  python benchmarks/run_bench.py --models openai/gpt-oss-20b qwen/qwen3.8-27b \
      --conditions sans_idc idc r_seule voi_seul --repeats 2
  python benchmarks/run_bench.py --mock --limit 5 --out /tmp/runs.jsonl

Résultats bruts : JSONL append-only (une ligne par run). Reprise automatique :
tout run_id déjà présent dans --out est sauté. Sur quota journalier Groq
(TPD/RPD), le modèle concerné est arrêté proprement et le reste est listé.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from idc_bench import HARNESS_VERSION  # noqa: E402
from idc_bench.client import (  # noqa: E402
    BenchGroqBackend,
    BenchHTTPError,
    QuotaExhausted,
    ScriptedBackend,
    list_groq_models,
)
from idc_bench.core import (  # noqa: E402
    CONDITION_ORDER,
    CONDITIONS,
    Params,
    auto_match,
    run_id,
    run_task,
    task_seed,
)

DEFAULT_TASKS = HERE / "tasks" / "idc_tasks_v1.jsonl"
DEFAULT_OUT = HERE / "results" / "live" / "runs.jsonl"
DEFAULT_MODELS = ["allam-2-7b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]


def load_tasks(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def done_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    ids.add(json.loads(line)["run_id"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return ids


def append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(rec, ensure_ascii=False) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        try:
            import fcntl  # verrou : plusieurs process (un par modèle) peuvent écrire

            fcntl.flock(f, fcntl.LOCK_EX)
        except (ImportError, OSError):
            pass
        f.write(line)
        f.flush()


def make_backend(model: str, seed: int, temperature: float, mock: bool):
    if mock:
        return ScriptedBackend(
            responses=[
                "Réponse simulée : Canberra est la capitale de l'Australie, siège du gouvernement fédéral depuis 1927 et ville planifiée.",
                "Réponse simulée : Canberra est la capitale de l'Australie, siège du gouvernement fédéral depuis 1927 et ville planifiée.",
            ],
            model=model,
        )
    return BenchGroqBackend.for_model(model, temperature=temperature, seed=seed)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--conditions", nargs="+", default=CONDITION_ORDER,
                    help=f"parmi {list(CONDITIONS)} ou 'all'")
    ap.add_argument("--repeats", type=int, default=1, help="nb TOTAL de répétitions visées (indices 0..N-1)")
    ap.add_argument("--limit", type=int, default=None, help="nb max de tâches (ordre du fichier)")
    ap.add_argument("--categories", nargs="*", default=None)
    ap.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--temperature", type=float, default=0.4)
    ap.add_argument("--max-runs", type=int, default=None, help="arrêt après N runs nouveaux (tous modèles)")
    ap.add_argument("--sleep", type=float, default=0.0, help="pause (s) entre runs")
    ap.add_argument("--mock", action="store_true", help="backend scripté, sans réseau")
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="affiche le plan sans appeler l'API")
    args = ap.parse_args(argv)

    if args.list_models:
        for m in sorted(list_groq_models(), key=lambda x: x["id"]):
            print(f"{m['id']}\t{m.get('owned_by')}\tctx={m.get('context_window')}\tactive={m.get('active')}")
        return 0

    conds = list(CONDITIONS) if args.conditions == ["all"] else args.conditions
    for c in conds:
        if c not in CONDITIONS:
            ap.error(f"condition inconnue : {c}")
    tasks = load_tasks(args.tasks)
    if args.categories:
        tasks = [t for t in tasks if t["category"] in args.categories]
    if args.limit:
        tasks = tasks[: args.limit]
    tasks_version = args.tasks.stem
    params = Params()
    done = done_ids(args.out)

    # Ordre : répétition → tâche (mélange déterministe par répétition, pour qu'un
    # arrêt sur quota laisse un échantillon couvrant toutes les catégories) →
    # condition (paires complètes Sans/Avec IDC) → modèle.
    plan = []
    for r in range(args.repeats):
        order = sorted(tasks, key=lambda t: hashlib.sha256(f"order|{r}|{t['id']}".encode()).hexdigest())
        plan += [(r, c, t, m) for t in order for c in conds for m in args.models]
    todo = [x for x in plan if run_id(x[3], x[1], x[2]["id"], x[0]) not in done]
    print(f"[plan] {len(plan)} runs visés, {len(plan) - len(todo)} déjà faits, {len(todo)} à faire "
          f"({len(tasks)} tâches × {len(conds)} conditions × {len(args.models)} modèles × {args.repeats} rép.)",
          flush=True)
    if args.dry_run:
        return 0

    exhausted: dict[str, str] = {}
    new_runs = 0
    for rep, cname, task, model in todo:
        if model in exhausted:
            continue
        if args.max_runs is not None and new_runs >= args.max_runs:
            break
        seed = task_seed(task["id"], rep)
        backend = make_backend(model, seed, args.temperature, args.mock)
        t0 = time.time()
        try:
            res = run_task(backend, task, CONDITIONS[cname], params)
        except QuotaExhausted as e:
            exhausted[model] = str(e)[:300]
            print(f"[quota] {model} arrêté : {str(e)[:160]}", flush=True)
            continue
        except BenchHTTPError as e:
            print(f"[erreur] {model} {cname} {task['id']} r{rep}: {str(e)[:200]} (non enregistré)", flush=True)
            continue
        rec = {
            "run_id": run_id(model, cname, task["id"], rep),
            "schema": "idc-bench-run/1",
            "harness_version": HARNESS_VERSION,
            "tasks_version": tasks_version,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "backend": "mock" if args.mock else "groq",
            "model": model,
            "condition": cname,
            "task_id": task["id"],
            "category": task["category"],
            "mode": task.get("mode", "single"),
            "expected_behavior": task["expected_behavior"],
            "repeat": rep,
            "seed": seed,
            "temperature": args.temperature,
            "reasoning_effort": getattr(backend, "reasoning_effort", None),
            "wall_s": round(time.time() - t0, 3),
            **res,
        }
        rec["auto_match"] = auto_match(rec["final_answer"], task.get("match") or [])
        append_jsonl(args.out, rec)
        new_runs += 1
        print(f"[ok] {model:22s} {cname:9s} {task['id']:9s} r{rep} steps={rec['steps']} "
              f"stop={rec['stop_reason']:8s} tok={rec['total_tokens']:5d} ign={rec['policy_ignorance']}",
              flush=True)
        if args.sleep:
            time.sleep(args.sleep)

    remaining = [x for x in todo if run_id(x[3], x[1], x[2]["id"], x[0]) not in done_ids(args.out)]
    print(f"[fin] {new_runs} nouveaux runs ; {len(remaining)} restants.", flush=True)
    for m, why in exhausted.items():
        n = sum(1 for x in remaining if x[3] == m)
        print(f"[reste] {m}: {n} runs non faits (quota) — relancer la même commande plus tard.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
