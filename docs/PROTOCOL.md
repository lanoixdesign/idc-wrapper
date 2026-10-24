# Protocole de recherche IDC — pré-enregistré (v1)

> **Statut** : pré-enregistrement v1, rédigé et publié **avant** l'analyse de la passe
> pilote. Toute modification ultérieure doit être datée dans la section
> [Journal des amendements](#10-journal-des-amendements) — on ne réécrit pas l'historique
> (le protocole lui-même est append-only, comme le journal IDC).
>
> **Objet** : tester empiriquement si l'enveloppe IDC (Effondrement Décisionnel
> Irréversible) — ressource finie `R`, journal append-only, règle d'arrêt VOI —
> améliore le comportement d'agents LLM réels. L'IDC est ici traité comme une
> **hypothèse**, pas comme un résultat acquis.

## 1. Questions de recherche

- **Q1** — Une ressource finie + règle d'arrêt réduit-elle le coût (tokens, appels)
  sans dégrader la qualité ?
- **Q2** — L'arrêt est-il **calibré** : ni boucle (révisions sans apport jusqu'au
  plafond), ni abandon prématuré (aveu d'ignorance sur une question à laquelle le
  modèle savait répondre) ?
- **Q3** — Sur des tâches multi-étapes, l'IDC limite-t-il la répétition / dérive ?
- **Q4** — En essaim (4 rôles, `R` partagée), l'IDC réduit-il la redondance et le coût ?
- **Q5** — Le journal permet-il de reconstruire chaque décision (traçabilité) ?
- **Q6** — L'IDC réduit-il les hallucinations et augmente-t-il l'abstention **correcte**
  (prémisses fausses, entités inexistantes, questions inconnaissables) ?
- **Q7** (exploratoire) — Quel pilier porte l'effet : `R` seule, VOI seul, ou leur
  combinaison ?

## 2. Hypothèses falsifiables

Notation : Δ = (Avec IDC) − (Sans IDC), même modèle, mêmes tâches, mêmes graines.

| # | Hypothèse | Métrique primaire | Réfutée si… |
|---|-----------|-------------------|-------------|
| **H1** (efficacité) | L'IDC réduit les tokens API totaux par tâche d'au moins 30 % **et** l'exactitude sur questions vérifiables ne baisse pas de plus de 5 points (non-infériorité). | tokens moyens / tâche ; exactitude juge | réduction < 30 % **ou** borne basse IC95 de Δexactitude < −5 pts |
| **H2** (calibration) | L'IDC diminue le taux d'atteinte du plafond de pas (`hit_cap`) sans augmenter l'abstention erronée de plus de 5 points. | `hit_cap` ; abstention erronée (ABSTAIN sur question vérifiable) | Δabstention_erronée IC95 borne haute > +5 pts, ou pas de baisse de `hit_cap` |
| **H3** (robustesse multi-étapes) | Sur `multistep`, l'IDC réduit le taux de boucle (`loop_flag`) et ne dégrade pas l'exactitude (marge 5 pts). | `loop_flag` ; exactitude | Δloop ≥ 0 ou Δexactitude borne basse < −5 pts |
| **H4** (essaim) | En essaim à `R` partagée, l'IDC réduit la redondance moyenne entre contributions et les tokens d'au moins 30 %. | `swarm_redundancy` ; tokens | Δredondance ≥ 0 ou réduction tokens < 30 % |
| **H5** (traçabilité) | 100 % des runs IDC ont un journal complet (une entrée par appel) et une raison d'arrêt explicite. | `journal_complete`, `stop_reason` | un seul run IDC sans journal complet |
| **H6** (honnêteté) | Sur les items non répondables (`false_premise`, `nonexistent`, `impossible`), l'IDC réduit le taux d'hallucination (McNemar apparié, p < 0,05) et augmente l'abstention correcte. | taux d'hallucination (juge) | pas de réduction significative sur la majorité des modèles |
| **H7** (ablation, exploratoire) | L'effet H6 requiert la combinaison R+VOI (R seule ou VOI seul < IDC). | idem H6 par condition | — (exploratoire, pas de test de confirmation) |

**Prédiction de non-effet assumée** : pour les modèles qui s'abstiennent déjà
spontanément (ex. `openai/gpt-oss-20b` en test manuel), on s'attend à un **effet
plafond** sur H6 ; un non-effet sur ces modèles n'est pas un échec de l'harness mais un
résultat.

## 3. Axes de mesure, tâches et métriques (définies à l'avance)

Jeu de tâches versionné : [`benchmarks/tasks/idc_tasks_v1.jsonl`](../benchmarks/tasks/idc_tasks_v1.jsonl)
(81 items construits pour ce projet, en français, aucun téléchargement).

| Catégorie | n | Comportement attendu | Axes |
|-----------|---|----------------------|------|
| `factual` | 20 | réponse vérifiable (référence + alias) | a, b, f |
| `false_premise` | 16 | signaler/corriger la prémisse | b, f |
| `nonexistent` | 12 | dire que l'entité (inventée) est inconnue | b, f |
| `impossible` | 10 | dire que c'est inconnaissable | b, f |
| `multistep` | 15 | calcul / raisonnement à plusieurs étapes, réponse unique | a, b, c |
| `swarm` | 8 | essaim de 4 rôles (7 vérifiables, 1 fictif à refuser) | a, d |

Tous les runs alimentent l'axe (e) traçabilité.

### (a) Efficacité qualité/ressource
- Primaire : tokens API totaux / tâche (prompt + complétion, valeurs `usage` Groq).
- Secondaires : appels / tâche, latence, exactitude par 1 000 tokens.

### (b) Calibration de l'arrêt
- Primaire : `hit_cap` (run arrivé au plafond de pas sans arrêt) et
  **abstention erronée** = verdict ABSTAIN sur un item `answer`.
- Secondaires : distribution de `stop_reason` (`cap`, `voi`, `resource`), `steps`.

### (c) Robustesse multi-étapes (boucles, dérive)
- Primaire : `loop_flag` = Jaccard lexical ≥ 0,8 entre deux sorties successives
  (révision sans apport). Exactitude sur `multistep`.
- Dérive : exactitude du pas final vs pas 1 (calculable depuis le journal).

### (d) Coordination en essaim, `R` partagée
- Primaire : `swarm_redundancy` = Jaccard moyen entre toutes les paires de contributions.
- Secondaires : tokens, tours, exactitude de la réponse du rédacteur.

### (e) Traçabilité
- Primaire : `journal_complete` (une entrée de journal par appel, append-only) et
  présence de `stop_reason`. Chaque run brut contient son journal complet.

### (f) Honnêteté / abstention
- Primaire : **taux d'hallucination** (juge) sur items non répondables.
- Secondaires : **abstention correcte** (verdict CORRECT sur `nonexistent`/`impossible`,
  ou ABSTAIN sur ces items ; CORRECT seul sur `false_premise`), hallucination sur items
  répondables.

## 4. Conditions

Même plafond de pas pour toutes les conditions (4 pas en mode simple, 2 rounds × 4 rôles
en essaim), même prompt de base, mêmes graines.

| Condition | `R` finie (+ notice de budget dans le prompt) | Règle VOI + aveu d'ignorance | Rôle |
|-----------|:---:|:---:|------|
| `sans_idc` | – | – | baseline : boucle de révision naïve |
| `r_seule` | ✔ | – | ablation |
| `voi_seul` | – | ✔ | ablation |
| `idc` | ✔ | ✔ | Avec IDC complet |

Paramètres (identiques à `idc.agent.IdcAgent`) : `R=100` (essaim : 200 partagée),
seuil critique 15, `cost_per_token=0.8` par mot produit (essaim : plafonné à 35/tour comme
`run_live.py`), coût marginal VOI = 40 (×2 si `R<30`), plancher « utile » = 40.
Gain VOI = `GroqBackend.gain_for_step` (heuristique lexicale **non validée**).

## 5. Modèles, répétitions, graines

- Modèles listés en direct via `GET https://api.groq.com/openai/v1/models`.
  Le 24/10/2026, modèles chat disponibles : `allam-2-7b`, `qwen/qwen3.8-27b`,
  `openai/gpt-oss-20b`, `openai/gpt-oss-120b` (+ modèles audio/garde-fous hors périmètre).
- Sujets : `allam-2-7b` (7B, SDAIA), `qwen/qwen3.8-27b` (27B, Alibaba),
  `openai/gpt-oss-20b` (MoE 20B, OpenAI) ; `openai/gpt-oss-120b` comme sujet quand le
  quota le permet (il sert aussi de juge, voir §6).
- Température 0,4 ; `seed = sha256(task_id|repeat)` identique entre conditions (paires) ;
  `reasoning_effort=low` pour les gpt-oss (économie de quota ; fixé pour toute l'étude).
- Pilote : 1 répétition. Phase confirmatoire : **≥ 5 répétitions** par modèle×condition,
  accumulées sur plusieurs jours (§8).

## 6. Juge aveugle

- Modèle : `openai/gpt-oss-120b` (le plus fort disponible sur Groq à date), température 0,
  sortie JSON, grille fixe `grid-v1` (`benchmarks/idc_bench/judge.py`).
- Aveugle : il ne voit ni le modèle, ni la condition, ni le journal, ni les tokens.
- Verdicts : `CORRECT` / `ABSTAIN` / `INCORRECT` + booléen `hallucination`.
- Le message d'aveu d'ignorance exact de l'IDC est classé par règle (ABSTAIN, sans
  hallucination) sans appel au juge — documenté, car ce message révèle la condition.
- Contrôles : (1) accord juge ↔ vérification automatique par alias de référence sur les
  items vérifiables (% accord, κ de Cohen) ; (2) **échantillon d'audit humain** (30 runs
  tirés au hasard, export aveugle `human_audit_sample.jsonl`) — objectif κ ≥ 0,7 ; tant
  que l'audit humain n'est pas fait, les résultats du juge sont **provisoires**.

## 7. Statistiques et critères

- Unité : run (modèle × condition × tâche × répétition).
- Intervalles : bootstrap percentile 95 %, 2 000 rééchantillonnages, **par tâche**
  (cluster bootstrap, les répétitions d'une tâche restent ensemble).
- Comparaisons appariées binaires (hallucination, exactitude, abstention) :
  test de **McNemar exact** (binomial bilatéral sur paires discordantes), paires
  (tâche, répétition) entre `sans_idc` et chaque autre condition, par modèle.
- Variables continues (tokens) : différence moyenne appariée + IC bootstrap.
- Pas de correction multiple dans le pilote (exploratoire) ; en confirmatoire, Holm sur
  H1–H6 par modèle.
- **Succès** d'une hypothèse : direction prédite + critère du tableau §2 rempli sur
  ≥ 2 modèles sur 3 en phase confirmatoire. **Échec** : critère de réfutation atteint
  sur ≥ 2 modèles. Sinon : non concluant.
- Le pilote (1 répétition) sert à vérifier l'harness et estimer les tailles d'effet ;
  **il ne valide ni ne réfute** aucune hypothèse.

## 8. Plan « longue durée »

- Routine quotidienne : relancer la **même commande** avec un nombre cible de répétitions
  élevé (ex. `--repeats 10`). La reprise saute tout `run_id` déjà présent
  (`sha256(modèle|condition|tâche|répétition)`) ; l'arrêt sur quota journalier est propre
  et la suite reprend le lendemain. Les résultats bruts s'accumulent dans un JSONL
  append-only, puis `judge_bench.py` et `analyze_bench.py` régénèrent `REPORT.md`.
- Ajout de modèles : nouvel identifiant dans `--models` ; jamais de réécriture des runs
  existants. Changement de jeu de tâches → nouveau fichier `idc_tasks_v2.jsonl`
  (les versions ne sont pas mélangées dans une même analyse).
- Arrêt de la phase confirmatoire : ≥ 5 répétitions complètes pour ≥ 3 modèles et
  audit humain fait.

## 9. Menaces à la validité

1. **Dépendance au modèle** : certains modèles (gpt-oss-20b) s'abstiennent déjà seuls →
   effet plafond ; d'autres (petits modèles) inventent quoi qu'il arrive. L'effet IDC,
   s'il existe, est probablement hétérogène.
2. **Heuristique VOI non validée** : le gain est un score lexical (nouveauté × longueur),
   pas une valeur d'information réelle. Il pénalise les réponses courtes (< 12 mots)
   — y compris correctes — et peut déclencher un aveu d'ignorance à tort. On mesure
   l'enveloppe telle qu'implémentée, pas « l'IDC idéal ».
3. **Confusion prompt / mécanisme** : la notice de budget (conditions à `R` finie)
   contient une phrase sur l'aveu d'ignorance ; une partie de l'effet peut venir du
   prompt plutôt que du mécanisme. Condition future proposée : `notice_seule`.
4. **Biais du juge** : même famille (gpt-oss) qu'un des sujets ; auto-préférence
   possible ; la règle ABSTAIN pour le message IDC révèle la condition ; grille unique.
   Mitigation : accord avec la référence automatique + audit humain.
5. **Quotas gratuits Groq** (≈ 8 000 tokens/min et quota journalier par modèle) : runs
   incomplets possibles ; l'ordre est mélangé par tâche et apparié par condition pour
   que tout arrêt laisse des paires complètes et un échantillon équilibré.
6. **Petits échantillons** : 81 items, 1 répétition au pilote → IC larges.
7. **Validité externe** : tâches courtes, en français, construites par nous ; la
   vérification automatique par alias (ex. chiffre « 2 ») est grossière.
8. **Non-déterminisme** de l'API (même avec `seed`) ; versions de modèles côté
   fournisseur qui peuvent changer sans préavis (on journalise l'horodatage).

## 10. Journal des amendements

- 2026-10-24 — v1 publiée (avant analyse du pilote).
