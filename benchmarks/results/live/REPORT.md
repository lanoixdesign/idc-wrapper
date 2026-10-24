# Rapport benchmark IDC — résultats live (Groq)

_Généré automatiquement par `benchmarks/analyze_bench.py` le 2026-10-24T01:39:18+00:00 (UTC) à partir des fichiers bruts `runs.jsonl` et `judgments.jsonl`. Aucun chiffre saisi à la main._

> **Avertissement** : passe pilote / exploratoire (voir `docs/PROTOCOL.md` §7). Intervalles = bootstrap 95 % par tâche. Juge LLM non encore validé par audit humain : les métriques issues du juge sont **provisoires**. Ne pas conclure à un gain général.

## 1. Avancement

| Modèle | sans_idc | idc | un_appel | jugés |
|---|---|---|---|---|
| allam-2-7b | 51 (1 rép.) | 51 (1 rép.) | 79 (1 rép.) | 84/181 |
| openai/gpt-oss-20b | 71 (1 rép.) | 71 (1 rép.) | 4 (1 rép.) | 144/146 |
| qwen/qwen3.8-27b | 59 (1 rép.) | 59 (1 rép.) | 61 (1 rép.) | 96/179 |

Tâches : 81 ({'factual': 20, 'false_premise': 16, 'nonexistent': 12, 'impossible': 10, 'multistep': 15, 'swarm': 8}). Runs totaux : 506. Jugements utilisés : 324 (dont 11 par règle « aveu d'ignorance IDC »).

## 2. Résultats par modèle × condition

Définitions (pré-enregistrées) : **Exact.** = verdict CORRECT sur items vérifiables (factual, multistep, swarm vérifiables) ; **Hallu. NR** = hallucination sur items non répondables (prémisse fausse, inexistant, impossible, swarm fictif) ; **Abst. correcte** = comportement attendu sur ces items ; **Abst. erronée** = ABSTAIN sur item vérifiable ; **Boucle** = Jaccard ≥ 0,8 entre deux sorties successives ; **Plafond** = arrêt au plafond de pas (trivialement 100 % pour `un_appel`, 1 pas).

| Modèle | Condition | n | Exact. | Hallu. NR | Abst. correcte | Abst. erronée | Tokens/tâche | Appels/tâche | Boucle | Plafond |
|---|---|---|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | 51 | 35 % [15–55] (n=20) | 68 % [47–89] (n=19) | 26 % [11–47] | 5 % [0–15] | 3186 [2660–3745] | 4.39 [4.08–4.71] | 55 % [41–69] | 100 % [100–100] |
| allam-2-7b | idc | 51 | 45 % [25–65] (n=20) | 61 % [39–83] (n=18) | 28 % [11–50] | 0 % [0–0] | 585 [515–661] | 1.20 [1.10–1.31] | 2 % [0–6] | 0 % [0–0] |
| allam-2-7b | un_appel | 79 | — (n=0) | 71 % [43–100] (n=7) | 29 % [0–57] | — | 483 [342–648] | 1.27 [1.08–1.46] | 3 % [0–6] | 100 % [100–100] |
| openai/gpt-oss-20b | sans_idc | 71 | 95 % [87–100] (n=38) | 39 % [24–55] (n=33) | 58 % [39–73] | 0 % [0–0] | 1886 [1585–2222] | 4.28 [4.06–4.56] | 79 % [69–87] | 100 % [100–100] |
| openai/gpt-oss-20b | idc | 71 | 97 % [92–100] (n=38) | 21 % [9–36] (n=33) | 79 % [64–91] | 0 % [0–0] | 688 [619–765] | 1.92 [1.82–2.01] | 18 % [10–27] | 0 % [0–0] |
| openai/gpt-oss-20b | un_appel | 4 | — (n=0) | 50 % [0–100] (n=2) | 50 % [0–100] | — | 233 [161–306] | 1.00 [1.00–1.00] | 0 % [0–0] | 100 % [100–100] |
| qwen/qwen3.8-27b | sans_idc | 59 | 91 % [78–100] (n=23) | 0 % [0–0] (n=21) | 100 % [100–100] | 0 % [0–0] | 1528 [1196–1935] | 4.34 [4.07–4.68] | 71 % [59–81] | 100 % [100–100] |
| qwen/qwen3.8-27b | idc | 59 | 100 % [100–100] (n=23) | 0 % [0–0] (n=21) | 100 % [100–100] | 0 % [0–0] | 546 [478–625] | 2.15 [2.02–2.29] | 8 % [2–15] | 0 % [0–0] |
| qwen/qwen3.8-27b | un_appel | 61 | 100 % [100–100] (n=1) | 0 % [0–0] (n=7) | 100 % [100–100] | 0 % [0–0] | 265 [155–392] | 1.25 [1.05–1.44] | 0 % [0–0] | 100 % [100–100] |

## 3. Exactitude par vérification automatique (alias de référence, sans juge)

| Modèle | Condition | Exact. auto (items vérifiables) |
|---|---|---|
| allam-2-7b | sans_idc | 46 % [29–64] (n=28) |
| allam-2-7b | idc | 54 % [36–71] (n=28) |
| allam-2-7b | un_appel | 63 % [49–78] (n=41) |
| openai/gpt-oss-20b | sans_idc | 97 % [92–100] (n=38) |
| openai/gpt-oss-20b | idc | 97 % [92–100] (n=38) |
| openai/gpt-oss-20b | un_appel | 100 % [100–100] (n=2) |
| qwen/qwen3.8-27b | sans_idc | 90 % [81–100] (n=31) |
| qwen/qwen3.8-27b | idc | 97 % [90–100] (n=31) |
| qwen/qwen3.8-27b | un_appel | 94 % [84–100] (n=31) |

## 4. Comparaisons appariées (McNemar exact, même tâche & répétition)

Référence A = `sans_idc` (hypothèses pré-enregistrées) ; comparaison secondaire `idc` vs `un_appel` (amendement 1). `A seul` = paires où seule la référence a l'issue ; `B seul` = seule la condition comparée l'a. Ratio tokens = moyenne appariée (B / A), IC bootstrap.

| Modèle | A (réf.) | B | Issue | paires | A seul | B seul | p |
|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | idc | hallucination (NR) | 18 | 3 | 2 | 1.000 |
| allam-2-7b | sans_idc | idc | exact (vérif.) | 20 | 1 | 3 | 0.625 |
| allam-2-7b | sans_idc | idc | abst. correcte (NR) | 18 | 1 | 1 | 1.000 |
| allam-2-7b | sans_idc | un_appel | hallucination (NR) | 7 | 0 | 0 | 1.000 |
| allam-2-7b | sans_idc | un_appel | abst. correcte (NR) | 7 | 0 | 0 | 1.000 |
| allam-2-7b | un_appel | idc | hallucination (NR) | 7 | 2 | 0 | 0.500 |
| allam-2-7b | un_appel | idc | abst. correcte (NR) | 7 | 0 | 1 | 1.000 |
| openai/gpt-oss-20b | sans_idc | idc | hallucination (NR) | 33 | 8 | 2 | 0.109 |
| openai/gpt-oss-20b | sans_idc | idc | exact (vérif.) | 38 | 0 | 1 | 1.000 |
| openai/gpt-oss-20b | sans_idc | idc | abst. correcte (NR) | 33 | 1 | 8 | 0.039 |
| openai/gpt-oss-20b | sans_idc | un_appel | hallucination (NR) | 2 | 0 | 0 | 1.000 |
| openai/gpt-oss-20b | sans_idc | un_appel | abst. correcte (NR) | 2 | 0 | 0 | 1.000 |
| openai/gpt-oss-20b | un_appel | idc | hallucination (NR) | 2 | 1 | 0 | 1.000 |
| openai/gpt-oss-20b | un_appel | idc | abst. correcte (NR) | 2 | 0 | 1 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | idc | hallucination (NR) | 21 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | idc | exact (vérif.) | 23 | 0 | 2 | 0.500 |
| qwen/qwen3.8-27b | sans_idc | idc | abst. correcte (NR) | 21 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | un_appel | hallucination (NR) | 7 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | un_appel | exact (vérif.) | 1 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | sans_idc | un_appel | abst. correcte (NR) | 7 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | un_appel | idc | hallucination (NR) | 7 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | un_appel | idc | exact (vérif.) | 1 | 0 | 0 | 1.000 |
| qwen/qwen3.8-27b | un_appel | idc | abst. correcte (NR) | 7 | 0 | 0 | 1.000 |

| Modèle | Ratio tokens | IC 95 % | paires |
|---|---|---|---|
| allam-2-7b | idc / sans_idc | 0.22 [0.19–0.25] | 51 |
| allam-2-7b | un_appel / sans_idc | 0.13 [0.12–0.15] | 51 |
| allam-2-7b | idc / un_appel | 1.91 [1.58–2.31] | 51 |
| openai/gpt-oss-20b | idc / sans_idc | 0.40 [0.38–0.43] | 71 |
| openai/gpt-oss-20b | un_appel / sans_idc | 0.15 [0.13–0.17] | 4 |
| openai/gpt-oss-20b | idc / un_appel | 2.51 [1.80–3.23] | 4 |
| qwen/qwen3.8-27b | idc / sans_idc | 0.42 [0.38–0.46] | 59 |
| qwen/qwen3.8-27b | un_appel / sans_idc | 0.13 [0.12–0.14] | 59 |
| qwen/qwen3.8-27b | idc / un_appel | 3.65 [3.23–4.10] | 59 |

## 5. Détail par catégorie (taux d'hallucination juge / comportement attendu)

| Modèle | Condition | factual | false_premise | impossible | multistep | nonexistent | swarm |
|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | hallu 3/7 · ok 4/7 | hallu 4/7 · ok 2/7 | hallu 4/6 · ok 2/6 | hallu 3/8 · ok 2/8 | hallu 5/6 · ok 1/6 | hallu 3/5 · ok 1/5 |
| allam-2-7b | idc | hallu 2/7 · ok 3/7 | hallu 3/7 · ok 2/7 | hallu 2/5 · ok 3/5 | hallu 3/8 · ok 4/8 | hallu 6/6 · ok 0/6 | hallu 2/5 · ok 2/5 |
| allam-2-7b | un_appel | — | hallu 1/2 · ok 1/2 | hallu 1/2 · ok 1/2 | — | hallu 3/3 · ok 0/3 | — |
| openai/gpt-oss-20b | sans_idc | hallu 0/19 · ok 19/19 | hallu 1/14 · ok 12/14 | hallu 2/8 · ok 6/8 | hallu 1/14 · ok 13/14 | hallu 10/11 · ok 1/11 | hallu 1/5 · ok 4/5 |
| openai/gpt-oss-20b | idc | hallu 0/19 · ok 19/19 | hallu 2/14 · ok 12/14 | hallu 2/8 · ok 6/8 | hallu 1/14 · ok 13/14 | hallu 3/11 · ok 8/11 | hallu 0/5 · ok 5/5 |
| openai/gpt-oss-20b | un_appel | — | — | hallu 0/1 · ok 1/1 | — | hallu 1/1 · ok 0/1 | — |
| qwen/qwen3.8-27b | sans_idc | hallu 1/8 · ok 7/8 | hallu 0/8 · ok 8/8 | hallu 0/7 · ok 7/7 | hallu 0/10 · ok 9/10 | hallu 0/6 · ok 6/6 | hallu 0/5 · ok 5/5 |
| qwen/qwen3.8-27b | idc | hallu 0/8 · ok 8/8 | hallu 0/8 · ok 8/8 | hallu 0/7 · ok 7/7 | hallu 0/10 · ok 10/10 | hallu 0/6 · ok 6/6 | hallu 0/5 · ok 5/5 |
| qwen/qwen3.8-27b | un_appel | hallu 0/1 · ok 1/1 | hallu 0/2 · ok 2/2 | hallu 0/2 · ok 2/2 | — | hallu 0/3 · ok 3/3 | — |

## 6. Arrêt, essaim, traçabilité

| Modèle | Condition | stop_reason | pas moyens | aveu IDC (politique) | redondance essaim | journal complet | sorties vides |
|---|---|---|---|---|---|---|---|
| allam-2-7b | sans_idc | {'cap': 51} | 4.39 [4.08–4.71] | 0/51 | 0.46 [0.38–0.53] (n=5) | 51/51 | 0 |
| allam-2-7b | idc | {'voi': 12, 'resource': 39} | 1.20 [1.10–1.31] | 0/51 | 0.46 [0.29–0.65] (n=5) | 51/51 | 0 |
| allam-2-7b | un_appel | {'cap': 79} | 1.27 [1.08–1.46] | 0/79 | 0.40 [0.30–0.51] (n=7) | 79/79 | 0 |
| openai/gpt-oss-20b | sans_idc | {'cap': 71} | 4.28 [4.06–4.56] | 0/71 | 0.33 [0.28–0.38] (n=5) | 71/71 | 0 |
| openai/gpt-oss-20b | idc | {'voi': 58, 'resource': 13} | 1.92 [1.82–2.01] | 8/71 | 0.33 [0.30–0.37] (n=5) | 71/71 | 0 |
| openai/gpt-oss-20b | un_appel | {'cap': 4} | 1.00 [1.00–1.00] | 0/4 | — (n=0) | 4/4 | 0 |
| qwen/qwen3.8-27b | sans_idc | {'cap': 59} | 4.34 [4.07–4.68] | 0/59 | 0.23 [0.21–0.25] (n=5) | 59/59 | 0 |
| qwen/qwen3.8-27b | idc | {'voi': 54, 'resource': 5} | 2.15 [2.02–2.29] | 4/59 | 0.25 [0.16–0.36] (n=5) | 59/59 | 0 |
| qwen/qwen3.8-27b | un_appel | {'cap': 61} | 1.25 [1.05–1.44] | 0/61 | 0.20 [0.18–0.23] (n=5) | 61/61 | 0 |

## 7. Contrôle du juge

Accord juge (CORRECT) ↔ vérification automatique par alias sur items vérifiables : 96.9 % sur 163 runs, κ = 0.89
La vérification par alias est elle-même grossière (ex. un chiffre isolé) : ce contrôle borne les erreurs grossières du juge, il ne remplace pas l'audit humain.

Échantillon d'audit humain exporté : `human_audit_sample.jsonl` (30 runs, aveugle à la condition et au verdict du juge). **Audit humain : non réalisé à ce jour.**

## 8. Limites rappelées

- Heuristique VOI lexicale non validée ; pénalise les réponses courtes.
- Juge de la même famille qu'un modèle testé ; règle ABSTAIN pour le message IDC.
- 1 répétition au pilote → IC larges ; quotas gratuits Groq ; tâches construites par nous.
- Voir `docs/PROTOCOL.md` §9 pour la liste complète.
