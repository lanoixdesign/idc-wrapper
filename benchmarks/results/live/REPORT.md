# Rapport benchmark IDC — résultats live (Groq)

_Généré automatiquement par `benchmarks/analyze_bench.py` le 2026-11-10T02:44:01+00:00 (UTC) à partir des fichiers bruts `runs.jsonl` et `judgments.jsonl`. Aucun chiffre saisi à la main._

> **Avertissement** : passe pilote / exploratoire (voir `docs/PROTOCOL.md` §7). Intervalles = bootstrap 95 % par tâche. Juge LLM non encore validé par audit humain : les métriques issues du juge sont **provisoires**. Ne pas conclure à un gain général.

## 1. Avancement

| Modèle | sans_idc | idc | un_appel | r_seule | voi_seul | jugés |
|---|---|---|---|---|---|---|
| allam-2-7b | 810 (10 rép.) | 810 (10 rép.) | 810 (10 rép.) | 810 (10 rép.) | 810 (10 rép.) | 339/4050 |
| openai/gpt-oss-20b | 462 (6 rép.) | 462 (6 rép.) | 462 (6 rép.) | 461 (6 rép.) | 461 (6 rép.) | 340/2308 |
| qwen/qwen3.8-27b | 691 (9 rép.) | 691 (9 rép.) | 690 (9 rép.) | 690 (9 rép.) | 690 (9 rép.) | 339/3452 |

Tâches : 81 ({'factual': 20, 'false_premise': 16, 'nonexistent': 12, 'impossible': 10, 'multistep': 15, 'swarm': 8}). Runs totaux : 9810. Jugements utilisés : 1018 (dont 17 par règle « aveu d'ignorance IDC »).

## 2. Résultats par modèle × condition

Définitions (pré-enregistrées) : **Exact.** = verdict CORRECT sur items vérifiables (factual, multistep, swarm vérifiables) ; **Hallu. NR** = hallucination sur items non répondables (prémisse fausse, inexistant, impossible, swarm fictif) ; **Abst. correcte** = comportement attendu sur ces items ; **Abst. erronée** = ABSTAIN sur item vérifiable ; **Boucle** = Jaccard ≥ 0,8 entre deux sorties successives ; **Plafond** = arrêt au plafond de pas (trivialement 100 % pour `un_appel`, 1 pas).

| Modèle | Condition | n | Exact. | Hallu. NR | Abst. correcte | Abst. erronée | Tokens/tâche | Appels/tâche | Boucle | Plafond |
|---|---|---|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | 810 | 40 % [26–55] (n=42) | 56 % [41–72] (n=39) | 38 % [23–54] | 2 % [0–7] | 3041 [2611–3505] | 4.40 [4.15–4.69] | 61 % [56–66] | 100 % [100–100] |
| allam-2-7b | idc | 810 | 50 % [36–64] (n=42) | 54 % [38–69] (n=39) | 38 % [23–54] | 0 % [0–0] | 617 [564–675] | 1.27 [1.20–1.34] | 2 % [1–3] | 0 % [0–0] |
| allam-2-7b | un_appel | 810 | 57 % [38–76] (n=21) | 67 % [51–82] (n=39) | 31 % [18–44] | 0 % [0–0] | 500 [353–669] | 1.30 [1.11–1.52] | 5 % [2–9] | 100 % [100–100] |
| allam-2-7b | r_seule | 810 | 55 % [35–75] (n=20) | 56 % [41–72] (n=39) | 36 % [21–51] | 0 % [0–0] | 1235 [861–1675] | 1.82 [1.52–2.16] | 10 % [4–15] | 0 % [0–1] |
| allam-2-7b | voi_seul | 810 | 63 % [42–84] (n=19) | 62 % [46–77] (n=39) | 33 % [21–49] | 0 % [0–0] | 819 [761–881] | 2.03 [2.00–2.08] | 11 % [8–14] | 0 % [0–0] |
| openai/gpt-oss-20b | sans_idc | 462 | 95 % [88–100] (n=42) | 36 % [21–51] (n=39) | 62 % [46–77] | 0 % [0–0] | 2058 [1713–2442] | 4.40 [4.15–4.69] | 81 % [75–86] | 100 % [100–100] |
| openai/gpt-oss-20b | idc | 462 | 95 % [88–100] (n=42) | 18 % [8–31] (n=39) | 82 % [69–92] | 2 % [0–7] | 701 [638–770] | 1.93 [1.85–2.01] | 21 % [15–26] | 0 % [0–0] |
| openai/gpt-oss-20b | un_appel | 462 | 95 % [86–100] (n=21) | 38 % [23–54] (n=39) | 59 % [44–74] | 0 % [0–0] | 428 [300–570] | 1.30 [1.11–1.52] | 3 % [0–6] | 100 % [100–100] |
| openai/gpt-oss-20b | r_seule | 461 | 100 % [100–100] (n=20) | 23 % [10–36] (n=39) | 77 % [64–90] | 0 % [0–0] | 1529 [1285–1793] | 3.39 [3.17–3.65] | 55 % [49–61] | 15 % [9–22] |
| openai/gpt-oss-20b | voi_seul | 461 | 100 % [100–100] (n=20) | 33 % [21–49] (n=39) | 64 % [49–79] | 0 % [0–0] | 654 [597–717] | 2.08 [2.03–2.13] | 33 % [27–39] | 0 % [0–0] |
| qwen/qwen3.8-27b | sans_idc | 691 | 93 % [86–100] (n=42) | 5 % [0–13] (n=39) | 95 % [87–100] | 0 % [0–0] | 1535 [1246–1858] | 4.39 [4.14–4.67] | 76 % [69–82] | 100 % [100–100] |
| qwen/qwen3.8-27b | idc | 691 | 98 % [93–100] (n=42) | 3 % [0–8] (n=39) | 97 % [92–100] | 0 % [0–0] | 516 [468–569] | 2.10 [2.02–2.18] | 10 % [7–14] | 0 % [0–0] |
| qwen/qwen3.8-27b | un_appel | 690 | 90 % [76–100] (n=21) | 3 % [0–8] (n=39) | 97 % [92–100] | 0 % [0–0] | 283 [182–399] | 1.29 [1.11–1.50] | 0 % [0–0] | 100 % [100–100] |
| qwen/qwen3.8-27b | r_seule | 690 | 100 % [100–100] (n=20) | 3 % [0–8] (n=39) | 97 % [92–100] | 0 % [0–0] | 1240 [1078–1424] | 3.87 [3.71–4.05] | 46 % [39–52] | 20 % [14–26] |
| qwen/qwen3.8-27b | voi_seul | 690 | 89 % [74–100] (n=19) | 3 % [0–8] (n=39) | 97 % [92–100] | 0 % [0–0] | 433 [386–483] | 2.10 [2.04–2.16] | 21 % [16–26] | 0 % [0–0] |

## 3. Exactitude par vérification automatique (alias de référence, sans juge)

| Modèle | Condition | Exact. auto (items vérifiables) |
|---|---|---|
| allam-2-7b | sans_idc | 63 % [51–75] (n=420) |
| allam-2-7b | idc | 59 % [47–70] (n=420) |
| allam-2-7b | un_appel | 65 % [52–76] (n=420) |
| allam-2-7b | r_seule | 60 % [48–72] (n=420) |
| allam-2-7b | voi_seul | 65 % [52–76] (n=420) |
| openai/gpt-oss-20b | sans_idc | 99 % [96–100] (n=236) |
| openai/gpt-oss-20b | idc | 98 % [95–100] (n=236) |
| openai/gpt-oss-20b | un_appel | 99 % [96–100] (n=236) |
| openai/gpt-oss-20b | r_seule | 99 % [96–100] (n=235) |
| openai/gpt-oss-20b | voi_seul | 98 % [94–100] (n=235) |
| qwen/qwen3.8-27b | sans_idc | 97 % [94–100] (n=356) |
| qwen/qwen3.8-27b | idc | 95 % [90–99] (n=356) |
| qwen/qwen3.8-27b | un_appel | 96 % [91–99] (n=355) |
| qwen/qwen3.8-27b | r_seule | 96 % [91–100] (n=355) |
| qwen/qwen3.8-27b | voi_seul | 96 % [91–99] (n=355) |

## 4. Comparaisons appariées (McNemar exact, même tâche & répétition)

Référence A = `sans_idc` (hypothèses pré-enregistrées) ; comparaison secondaire `idc` vs `un_appel` (amendement 1). `A seul` = paires où seule la référence a l'issue ; `B seul` = seule la condition comparée l'a. Ratio tokens = moyenne appariée (B / A), IC bootstrap.

| Modèle | A (réf.) | B | Issue | paires | A seul | B seul | p |
|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | idc | hallucination (NR) | 39 | 5 | 4 | 1.000 |
| allam-2-7b | sans_idc | idc | exact (vérif.) | 42 | 3 | 7 | 0.344 |
| allam-2-7b | sans_idc | idc | abst. correcte (NR) | 39 | 4 | 4 | 1.000 |
| allam-2-7b | sans_idc | un_appel | hallucination (NR) | 39 | 0 | 4 | 0.125 |
| allam-2-7b | sans_idc | un_appel | exact (vérif.) | 21 | 1 | 1 | 1.000 |
| allam-2-7b | sans_idc | un_appel | abst. correcte (NR) | 39 | 4 | 1 | 0.375 |
| allam-2-7b | sans_idc | r_seule | hallucination (NR) | 39 | 4 | 4 | 1.000 |
| allam-2-7b | sans_idc | r_seule | exact (vérif.) | 20 | 4 | 3 | 1.000 |
| allam-2-7b | sans_idc | r_seule | abst. correcte (NR) | 39 | 4 | 3 | 1.000 |
| allam-2-7b | sans_idc | voi_seul | hallucination (NR) | 39 | 0 | 2 | 0.500 |
| allam-2-7b | sans_idc | voi_seul | exact (vérif.) | 19 | 0 | 1 | 1.000 |
| allam-2-7b | sans_idc | voi_seul | abst. correcte (NR) | 39 | 2 | 0 | 0.500 |
| allam-2-7b | un_appel | idc | hallucination (NR) | 39 | 7 | 2 | 0.180 |
| allam-2-7b | un_appel | idc | exact (vérif.) | 21 | 2 | 3 | 1.000 |
| allam-2-7b | un_appel | idc | abst. correcte (NR) | 39 | 3 | 6 | 0.508 |
| openai/gpt-oss-20b | sans_idc | idc | hallucination (NR) | 39 | 9 | 2 | 0.065 |
| openai/gpt-oss-20b | sans_idc | idc | exact (vérif.) | 42 | 1 | 1 | 1.000 |
| openai/gpt-oss-20b | sans_idc | idc | abst. correcte (NR) | 39 | 1 | 9 | 0.021 |
| openai/gpt-oss-20b | sans_idc | un_appel | hallucination (NR) | 39 | 0 | 1 | 1.000 |
| openai/gpt-oss-20b | sans_idc | un_appel | exact (vérif.) | 21 | 1 | 0 | 1.000 |
| openai/gpt-oss-20b | sans_idc | un_appel | abst. correcte (NR) | 39 | 1 | 0 | 1.000 |
| openai/gpt-oss-20b | sans_idc | r_seule | hallucination (NR) | 39 | 5 | 0 | 0.062 |
| openai/gpt-oss-20b | sans_idc | r_seule | exact (vérif.) | 20 | 0 | 0 | 1.000 |
| openai/gpt-oss-20b | sans_idc | r_seule | abst. correcte (NR) | 39 | 0 | 6 | 0.031 |
| openai/gpt-oss-20b | sans_idc | voi_seul | hallucination (NR) | 39 | 1 | 0 | 1.000 |
| openai/gpt-oss-20b | sans_idc | voi_seul | exact (vérif.) | 20 | 0 | 0 | 1.000 |
| openai/gpt-oss-20b | sans_idc | voi_seul | abst. correcte (NR) | 39 | 0 | 1 | 1.000 |
| openai/gpt-oss-20b | un_appel | idc | hallucination (NR) | 39 | 10 | 2 | 0.039 |
| openai/gpt-oss-20b | un_appel | idc | exact (vérif.) | 21 | 0 | 1 | 1.000 |
| openai/gpt-oss-20b | un_appel | idc | abst. correcte (NR) | 39 | 1 | 10 | 0.012 |
| qwen/qwen3.8-27b | sans_idc | idc | hallucination (NR) | 39 | 1 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | idc | exact (vérif.) | 42 | 0 | 2 | 0.500 |
| qwen/qwen3.8-27b | sans_idc | idc | abst. correcte (NR) | 39 | 0 | 1 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | un_appel | hallucination (NR) | 39 | 1 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | un_appel | exact (vérif.) | 21 | 1 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | un_appel | abst. correcte (NR) | 39 | 0 | 1 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | r_seule | hallucination (NR) | 39 | 1 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | r_seule | exact (vérif.) | 20 | 0 | 1 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | r_seule | abst. correcte (NR) | 39 | 0 | 1 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | voi_seul | hallucination (NR) | 39 | 1 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | voi_seul | exact (vérif.) | 19 | 1 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | voi_seul | abst. correcte (NR) | 39 | 0 | 1 | 1.000 |
| qwen/qwen3.8-27b | un_appel | idc | hallucination (NR) | 39 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | un_appel | idc | exact (vérif.) | 21 | 0 | 2 | 0.500 |
| qwen/qwen3.8-27b | un_appel | idc | abst. correcte (NR) | 39 | 0 | 0 | 1.000 |

| Modèle | Ratio tokens | IC 95 % | paires |
|---|---|---|---|
| allam-2-7b | idc / sans_idc | 0.24 [0.22–0.26] | 810 |
| allam-2-7b | un_appel / sans_idc | 0.13 [0.12–0.14] | 810 |
| allam-2-7b | r_seule / sans_idc | 0.35 [0.31–0.39] | 810 |
| allam-2-7b | voi_seul / sans_idc | 0.30 [0.29–0.31] | 810 |
| allam-2-7b | idc / un_appel | 2.16 [1.95–2.39] | 810 |
| openai/gpt-oss-20b | idc / sans_idc | 0.40 [0.37–0.42] | 462 |
| openai/gpt-oss-20b | un_appel / sans_idc | 0.17 [0.16–0.18] | 462 |
| openai/gpt-oss-20b | r_seule / sans_idc | 0.79 [0.74–0.85] | 461 |
| openai/gpt-oss-20b | voi_seul / sans_idc | 0.36 [0.34–0.37] | 461 |
| openai/gpt-oss-20b | idc / un_appel | 2.60 [2.39–2.81] | 462 |
| qwen/qwen3.8-27b | idc / sans_idc | 0.40 [0.38–0.42] | 691 |
| qwen/qwen3.8-27b | un_appel / sans_idc | 0.13 [0.12–0.15] | 690 |
| qwen/qwen3.8-27b | r_seule / sans_idc | 0.91 [0.86–0.95] | 690 |
| qwen/qwen3.8-27b | voi_seul / sans_idc | 0.32 [0.31–0.33] | 690 |
| qwen/qwen3.8-27b | idc / un_appel | 3.45 [3.18–3.73] | 690 |

## 5. Détail par catégorie (taux d'hallucination juge / comportement attendu)

| Modèle | Condition | factual | false_premise | impossible | multistep | nonexistent | swarm |
|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | hallu 8/20 · ok 12/20 | hallu 8/16 · ok 7/16 | hallu 4/10 · ok 6/10 | hallu 6/15 · ok 3/15 | hallu 10/12 · ok 2/12 | hallu 4/8 · ok 2/8 |
| allam-2-7b | idc | hallu 6/20 · ok 12/20 | hallu 7/16 · ok 6/16 | hallu 3/10 · ok 7/10 | hallu 7/15 · ok 6/15 | hallu 11/12 · ok 1/12 | hallu 3/8 · ok 4/8 |
| allam-2-7b | un_appel | hallu 8/20 · ok 12/20 | hallu 10/16 · ok 6/16 | hallu 5/10 · ok 5/10 | hallu 0/1 · ok 0/1 | hallu 11/12 · ok 1/12 | hallu 0/1 · ok 0/1 |
| allam-2-7b | r_seule | hallu 6/20 · ok 11/20 | hallu 8/16 · ok 5/16 | hallu 3/10 · ok 7/10 | — | hallu 11/12 · ok 1/12 | hallu 0/1 · ok 1/1 |
| allam-2-7b | voi_seul | hallu 7/19 · ok 12/19 | hallu 9/16 · ok 7/16 | hallu 4/10 · ok 5/10 | — | hallu 11/12 · ok 1/12 | hallu 0/1 · ok 0/1 |
| openai/gpt-oss-20b | sans_idc | hallu 0/20 · ok 20/20 | hallu 1/16 · ok 14/16 | hallu 2/10 · ok 8/10 | hallu 1/15 · ok 14/15 | hallu 11/12 · ok 1/12 | hallu 1/8 · ok 7/8 |
| openai/gpt-oss-20b | idc | hallu 0/20 · ok 20/20 | hallu 2/16 · ok 14/16 | hallu 2/10 · ok 8/10 | hallu 1/15 · ok 14/15 | hallu 3/12 · ok 9/12 | hallu 0/8 · ok 7/8 |
| openai/gpt-oss-20b | un_appel | hallu 1/20 · ok 19/20 | hallu 2/16 · ok 13/16 | hallu 2/10 · ok 8/10 | hallu 0/1 · ok 1/1 | hallu 11/12 · ok 1/12 | hallu 0/1 · ok 1/1 |
| openai/gpt-oss-20b | r_seule | hallu 0/20 · ok 20/20 | hallu 1/16 · ok 15/16 | hallu 1/10 · ok 9/10 | — | hallu 7/12 · ok 5/12 | hallu 0/1 · ok 1/1 |
| openai/gpt-oss-20b | voi_seul | hallu 0/20 · ok 20/20 | hallu 1/16 · ok 14/16 | hallu 2/10 · ok 8/10 | — | hallu 10/12 · ok 2/12 | hallu 0/1 · ok 1/1 |
| qwen/qwen3.8-27b | sans_idc | hallu 1/20 · ok 19/20 | hallu 1/16 · ok 15/16 | hallu 0/10 · ok 10/10 | hallu 1/15 · ok 13/15 | hallu 1/12 · ok 11/12 | hallu 0/8 · ok 8/8 |
| qwen/qwen3.8-27b | idc | hallu 0/20 · ok 20/20 | hallu 1/16 · ok 15/16 | hallu 0/10 · ok 10/10 | hallu 1/15 · ok 14/15 | hallu 0/12 · ok 12/12 | hallu 0/8 · ok 8/8 |
| qwen/qwen3.8-27b | un_appel | hallu 2/20 · ok 18/20 | hallu 1/16 · ok 15/16 | hallu 0/10 · ok 10/10 | hallu 0/1 · ok 1/1 | hallu 0/12 · ok 12/12 | hallu 0/1 · ok 1/1 |
| qwen/qwen3.8-27b | r_seule | hallu 0/20 · ok 20/20 | hallu 1/16 · ok 15/16 | hallu 0/10 · ok 10/10 | — | hallu 0/12 · ok 12/12 | hallu 0/1 · ok 1/1 |
| qwen/qwen3.8-27b | voi_seul | hallu 2/19 · ok 17/19 | hallu 1/16 · ok 15/16 | hallu 0/10 · ok 10/10 | — | hallu 0/12 · ok 12/12 | hallu 0/1 · ok 1/1 |

## 6. Arrêt, essaim, traçabilité

| Modèle | Condition | stop_reason | pas moyens | aveu IDC (politique) | redondance essaim | journal complet | sorties vides |
|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | {'cap': 810} | 4.40 [4.15–4.69] | 0/810 | 0.50 [0.44–0.56] (n=80) | 810/810 | 0 |
| allam-2-7b | idc | {'voi': 200, 'resource': 610} | 1.27 [1.20–1.34] | 3/810 | 0.44 [0.37–0.52] (n=77) | 810/810 | 0 |
| allam-2-7b | un_appel | {'cap': 810} | 1.30 [1.11–1.52] | 0/810 | 0.49 [0.40–0.58] (n=80) | 810/810 | 0 |
| allam-2-7b | r_seule | {'resource': 808, 'cap': 2} | 1.82 [1.52–2.16] | 0/810 | 0.52 [0.47–0.58] (n=80) | 810/810 | 0 |
| allam-2-7b | voi_seul | {'voi': 810} | 2.03 [2.00–2.08] | 8/810 | 0.43 [0.32–0.53] (n=80) | 810/810 | 0 |
| openai/gpt-oss-20b | sans_idc | {'cap': 462} | 4.40 [4.15–4.69] | 0/462 | 0.42 [0.36–0.48] (n=46) | 462/462 | 0 |
| openai/gpt-oss-20b | idc | {'voi': 372, 'resource': 90} | 1.93 [1.85–2.01] | 52/462 | 0.30 [0.27–0.33] (n=44) | 462/462 | 0 |
| openai/gpt-oss-20b | un_appel | {'cap': 462} | 1.30 [1.11–1.52] | 0/462 | 0.33 [0.28–0.38] (n=46) | 462/462 | 0 |
| openai/gpt-oss-20b | r_seule | {'resource': 392, 'cap': 69} | 3.39 [3.17–3.65] | 0/461 | 0.40 [0.35–0.44] (n=46) | 461/461 | 2 |
| openai/gpt-oss-20b | voi_seul | {'voi': 461} | 2.08 [2.03–2.13] | 3/461 | 0.28 [0.25–0.31] (n=43) | 461/461 | 1 |
| qwen/qwen3.8-27b | sans_idc | {'cap': 691} | 4.39 [4.14–4.67] | 0/691 | 0.22 [0.20–0.24] (n=67) | 691/691 | 0 |
| qwen/qwen3.8-27b | idc | {'voi': 656, 'resource': 35} | 2.10 [2.02–2.18] | 46/691 | 0.25 [0.23–0.28] (n=67) | 691/691 | 0 |
| qwen/qwen3.8-27b | un_appel | {'cap': 690} | 1.29 [1.11–1.50] | 0/690 | 0.19 [0.18–0.21] (n=67) | 690/690 | 0 |
| qwen/qwen3.8-27b | r_seule | {'resource': 551, 'cap': 139} | 3.87 [3.71–4.05] | 0/690 | 0.20 [0.19–0.22] (n=67) | 690/690 | 0 |
| qwen/qwen3.8-27b | voi_seul | {'voi': 690} | 2.10 [2.04–2.16] | 0/690 | 0.26 [0.24–0.29] (n=67) | 690/690 | 0 |

## 7. Contrôle du juge

Accord juge (CORRECT) ↔ vérification automatique par alias sur items vérifiables : 94.0 % sur 432 runs, κ = 0.78
La vérification par alias est elle-même grossière (ex. un chiffre isolé) : ce contrôle borne les erreurs grossières du juge, il ne remplace pas l'audit humain.

Échantillon d'audit humain exporté : `human_audit_sample.jsonl` (30 runs, aveugle à la condition et au verdict du juge). **Audit humain : non réalisé à ce jour.**

## 8. Limites rappelées

- Heuristique VOI lexicale non validée ; pénalise les réponses courtes.
- Juge de la même famille qu'un modèle testé ; règle ABSTAIN pour le message IDC.
- 1 répétition au pilote → IC larges ; quotas gratuits Groq ; tâches construites par nous.
- **Couverture du juge partielle et non aléatoire** quand le quota du juge s'épuise : les items non répondables sont jugés en priorité ; les colonnes issues du juge portent alors sur un sous-ensemble (voir les n) et ne sont pas comparables aux colonnes auto.
- **Comparaisons multiples** : ~27 tests McNemar non corrigés ; un p < 0,05 isolé n'est pas une preuve (pré-enregistré : seuls H1–H7, à confirmer en passe longue).
- Voir `docs/PROTOCOL.md` §9 pour la liste complète.
