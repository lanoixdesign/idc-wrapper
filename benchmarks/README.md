# Benchmarks IDC

Deux familles :

| Fichier | Rôle | Réseau |
|---------|------|--------|
| `bench_mock.py`, `write_performance_md.py` | micro-bench historique sur LLM factice (→ `PERFORMANCE.md`) | non |
| `run_bench.py`, `judge_bench.py`, `analyze_bench.py`, `idc_bench/` | **harness de recherche** live Groq (protocole [`docs/PROTOCOL.md`](../docs/PROTOCOL.md)) | oui (Groq) |
| `tasks/idc_tasks_v1.jsonl` | jeu de tâches versionné (81 items) | — |
| `results/live/` | résultats bruts append-only + `REPORT.md` | — |
| `tests/test_harness.py` | tests CI sans réseau | non |

## Conditions

`sans_idc` (boucle de révision naïve) · `r_seule` (ressource finie seule) ·
`voi_seul` (règle d'arrêt VOI + aveu d'ignorance seuls) · `idc` (R + VOI). Même plafond
de pas pour toutes. Détails : `idc_bench/core.py` et `docs/PROTOCOL.md` §4.

## Lancer

```bash
export GROQ_API_KEY=...            # jamais commitée, jamais loggée
python3 benchmarks/run_bench.py --list-models

# Une passe (reprise automatique : les run_id déjà présents sont sautés)
python3 benchmarks/run_bench.py \
  --models allam-2-7b qwen/qwen3.8-27b openai/gpt-oss-20b \
  --conditions sans_idc idc r_seule voi_seul --repeats 1

# Juge aveugle (gpt-oss-120b, grille fixe grid-v1), puis rapport
python3 benchmarks/judge_bench.py
python3 benchmarks/analyze_bench.py      # → benchmarks/results/live/REPORT.md
```

Options utiles : `--limit N` (N premières tâches), `--categories factual multistep`,
`--max-runs N`, `--out chemin.jsonl`, `--mock` (sans réseau), `--dry-run` (plan seul).

Plusieurs process (un par modèle) peuvent écrire dans le même JSONL (verrou `flock`) ;
c'est recommandé car les quotas Groq sont par modèle.

## Format des résultats

`results/live/runs.jsonl` — une ligne par run : `run_id`, `model`, `condition`,
`task_id`, `category`, `repeat`, `seed`, `final_answer`, `steps`, `stop_reason`
(`cap`/`voi`/`resource`), `calls`, `prompt_tokens`, `completion_tokens`,
`reasoning_tokens`, `total_tokens`, `latency_s`, `loop_flag`, `hit_cap`,
`swarm_redundancy`, `policy_ignorance`, `journal` (complet), `auto_match`,
`timestamp_utc`…

`results/live/judgments.jsonl` — une ligne par run jugé : `verdict`
(`CORRECT`/`ABSTAIN`/`INCORRECT`), `hallucination`, `raison`, `judge_model`, `grid`.

Ces fichiers sont **append-only** : on ne les réécrit pas, on ajoute.

## Quotas Groq (offre gratuite)

Limites observées le 24/10/2026 via les en-têtes `x-ratelimit-*` : ~8 000 tokens/min
et 1 000 requêtes/jour pour `gpt-oss-*` et `qwen3.8-27b`, 6 000 tokens/min pour
`allam-2-7b`, plus un quota journalier de tokens. Le client fait du backoff sur 429 ;
sur quota journalier épuisé il arrête proprement le modèle et affiche ce qui reste.
Relancer la même commande le lendemain reprend où l'on s'était arrêté.

## Limites du juge

Voir `docs/PROTOCOL.md` §6 et §9 : même famille qu'un sujet (gpt-oss), grille unique,
message d'aveu d'ignorance IDC classé par règle, audit humain à faire
(`results/live/human_audit_sample.jsonl`).
