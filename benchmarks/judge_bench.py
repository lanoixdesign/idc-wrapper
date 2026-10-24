#!/usr/bin/env python3
"""Juge les runs non encore jugés (append-only, reprise, cache par réponse).

  python benchmarks/judge_bench.py --runs benchmarks/results/live/runs.jsonl \
      --judge-model openai/gpt-oss-120b

Priorité : conditions sans_idc et idc d'abord, puis ablations. Une même
(tâche, réponse normalisée) n'est jugée qu'une fois (cache).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from idc_bench.client import BenchGroqBackend, BenchHTTPError, QuotaExhausted  # noqa: E402
from idc_bench.core import CONDITION_ORDER, IGNORANCE_MSG, normalize  # noqa: E402
from idc_bench.judge import JUDGE_GRID_VERSION, build_judge_prompt, parse_judgment  # noqa: E402
from run_bench import DEFAULT_OUT, DEFAULT_TASKS, append_jsonl, load_tasks  # noqa: E402


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def answer_key(task_id: str, answer: str) -> str:
    return hashlib.sha256(f"{task_id}|{normalize(answer).strip()}".encode()).hexdigest()[:20]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=Path, nargs="+", default=[DEFAULT_OUT])
    ap.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    ap.add_argument("--out", type=Path, default=None, help="défaut : judgments.jsonl à côté du 1er --runs")
    ap.add_argument("--judge-model", default="openai/gpt-oss-120b")
    ap.add_argument("--max-calls", type=int, default=None)
    args = ap.parse_args(argv)
    out = args.out or args.runs[0].parent / "judgments.jsonl"
    tasks = {t["id"]: t for t in load_tasks(args.tasks)}
    runs = [r for p in args.runs for r in read_jsonl(p)]
    judged = {j["run_id"] for j in read_jsonl(out) if j.get("judge_model") in (args.judge_model, "rule")}
    cache = {j["answer_key"]: j for j in read_jsonl(out) if j.get("judge_model") == args.judge_model}
    prio = {c: i for i, c in enumerate(CONDITION_ORDER)}
    # Priorité : items non répondables d'abord (pas de vérification automatique possible),
    # puis par tâche pour compléter les paires de conditions, conditions principales d'abord.
    todo = sorted([r for r in runs if r["run_id"] not in judged],
                  key=lambda r: (r.get("repeat", 0), r["expected_behavior"] == "answer",
                                 min(prio.get(r["condition"], 9), 2), r["task_id"],
                                 prio.get(r["condition"], 9)))
    print(f"[juge] {len(todo)} runs à juger ({len(judged)} déjà jugés)", flush=True)
    backend = BenchGroqBackend.for_model(args.judge_model, temperature=0.0, json_mode=True)
    calls = 0
    for r in todo:
        task = tasks[r["task_id"]]
        key = answer_key(r["task_id"], r["final_answer"])
        base = {"run_id": r["run_id"], "task_id": r["task_id"], "answer_key": key,
                "grid": JUDGE_GRID_VERSION,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        if r["final_answer"].strip() == IGNORANCE_MSG:
            append_jsonl(out, {**base, "judge_model": "rule", "verdict": "ABSTAIN",
                               "hallucination": False, "raison": "message d'aveu d'ignorance IDC"})
            continue
        if key in cache:
            c = cache[key]
            append_jsonl(out, {**base, "judge_model": args.judge_model, "verdict": c["verdict"],
                               "hallucination": c["hallucination"], "raison": c["raison"], "cached": True})
            continue
        if args.max_calls is not None and calls >= args.max_calls:
            break
        parsed = None
        try:
            for _ in range(2):
                info = backend.call(build_judge_prompt(task, r["final_answer"]), max_tokens=700)
                calls += 1
                parsed = parse_judgment(info.content)
                if parsed:
                    break
        except QuotaExhausted as e:
            print(f"[quota juge] arrêt : {str(e)[:160]}", flush=True)
            break
        except BenchHTTPError as e:
            print(f"[erreur juge] {r['run_id']}: {str(e)[:160]}", flush=True)
            continue
        if not parsed:
            print(f"[juge] sortie illisible pour {r['run_id']} — ignoré", flush=True)
            continue
        rec = {**base, "judge_model": args.judge_model, **parsed}
        cache[key] = rec
        append_jsonl(out, rec)
        print(f"[juge] {r['model']:22s} {r['condition']:9s} {r['task_id']:9s} → {parsed['verdict']:9s} "
              f"hallu={parsed['hallucination']}", flush=True)
    print(f"[juge fin] {calls} appels juge", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
