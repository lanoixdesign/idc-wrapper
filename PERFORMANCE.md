# PERFORMANCE — mesures mock reproductibles

> **Avertissement** : ces chiffres viennent d’un **LLM mock déterministe**
> (`benchmarks/bench_mock.py`), exécuté sur une machine de développement.
> Ce ne sont **pas** des FLOPS, ni des taux de survie, ni des résultats sur
> GPT/Claude/Llama en production. Toute affirmation empirique plus forte
> serait une invention.

## Comment reproduire

```bash
# depuis la racine du dépôt
PYTHONPATH=python python3 benchmarks/bench_mock.py
PYTHONPATH=python python3 benchmarks/write_performance_md.py   # régénère ce fichier
PYTHONPATH=python python3 -m unittest discover -s python/idc -v
```

Aucune clé API n’est requise.

## Métadonnées de la dernière exécution

| Champ | Valeur |
|-------|--------|
| Généré (UTC) | `2026-10-23T10:50:28.400673+00:00` |
| Python | 3.13.5 |
| Plateforme | Linux-6.12.94+-x86_64-with-glibc2.41 |
| Version IDC packagée | 0.2.0 |

## Métriques

| Métrique | Définition |
|----------|------------|
| **Étapes** | Nombre d’appels backend dans la boucle (`max_steps` = 8). |
| **Tokens≈** | Approximation `len(chunk.split())` (pas un tokenizer réel). |
| **R finale** | Ressource restante après coûts (`cost = tokens≈ × cost_per_token`). |
| **Coût** | Somme des coûts d’étape (unité arbitraire de ressource). |
| **Arrêt anticipé** | IDC s’est arrêté avant `max_steps` via VOI / seuil. |
| **Ignorance** | Réponse finale = aveu (« Je ne sais pas… ») plutôt qu’invention. |
| **Taux d’ignorance forcée (incertitude)** | Sur variantes de budget du scénario `uncertain` : fraction des runs qui avouent l’ignorance. |

## Résultats (dernière run)

| Scénario | Mode | Étapes | Tokens≈ | R finale | Coût | Arrêt anticipé | Ignorance |
|----------|------|--------|---------|----------|------|----------------|-----------|
| support_client | baseline | 8 | 67 | 46.4 | 53.6 | non | non |
| support_client | idc | 4 | 36 | 71.2 | 28.8 | oui | non |
| code_assistant | baseline | 8 | 45 | 64.0 | 36.0 | non | non |
| code_assistant | idc | 4 | 31 | 75.2 | 24.8 | oui | non |
| research_synth | baseline | 8 | 44 | 64.8 | 35.2 | non | non |
| research_synth | idc | 4 | 32 | 74.4 | 25.6 | oui | non |
| verbose | baseline | 8 | 60 | 52.0 | 48.0 | non | non |
| verbose | idc | 4 | 33 | 73.6 | 26.4 | oui | non |
| uncertain | baseline | 8 | 8 | 93.6 | 6.4 | non | oui |
| uncertain | idc | 1 | 1 | 99.2 | 0.8 | oui | oui |

### Agrégats

| Agrégat | Baseline | IDC |
|---------|----------|-----|
| Étapes moyennes | 8.0 | 3.4 |
| Tokens≈ moyens | 44.8 | 26.6 |
| R finale moyenne | 64.16 | 78.72 |
| Taux ignorance (`uncertain`, 5 budgets) | 1.0 | 1.0 |

Lecture honnête sur ce mock :

- **IDC coupe la boucle** : ~3.4 étapes vs 8.0 en baseline ; les étapes « hallucination / digression » des scénarios ne sont pas atteintes.
- **Ressource préservée** : R finale moyenne plus haute sous IDC (78.72 vs 64.16).
- **Incertitude** : réponses vides → les deux modes avouent l’ignorance ; la différence visible est le **nombre d’étapes brûlées** (IDC : 1, baseline : 8 sur le run principal).

## Ce que le code démontre vs ce que le livre hypothese

| Affirmation | Statut |
|-------------|--------|
| Une règle d’arrêt VOI vs coût marginal réduit les étapes sur un mock scripté | **Démontré ici** (voir tableau) |
| Journal append-only + décroissance de R sont implémentables de façon portable | **Démontré** (Rust + Python) |
| Sous incertitude, l’aveu d’ignorance peut être préféré à l’invention | **Illustré** sur mock `uncertain` (pas une preuve LLM) |
| Formalisme type Lindblad / finitude / « urgence d’exister » explique l’AGI | **Hypothèse théorique** (ouvrage / modèle) — **non prouvée** par ce dépôt |
| IDC réduit les hallucinations sur modèles de frontier | **Non mesuré** ici — protocole futur, pas un fait |
| Chiffres de survie / FLOPS / win-rate agents | **Absents volontairement** — ne pas les inventer |

Références conceptuelles (hypothèses, pas preuves empiriques de ce repo) :

- Finitude computationnelle et arrêt optimal comme contrainte vitale.
- Engagement irréversible (journal append-only) vs backtracking « gratuit ».
- Coût asymétrique : inventer une réalité ne doit pas être moins cher qu’avouer l’ignorance.

## Limites (caveats)

1. Le backend est **scripté** : les gains VOI sont fournis par le scénario, pas estimés par un modèle.
2. `tokens≈` ≠ tokens BPE/SentencePiece.
3. La heuristique `gain > cost_per_token * 50 * risk` est volontairement simple.
4. CI et benches locaux ne remplacent pas une étude sur API réelles.
5. Ne citez pas ce fichier comme validation empirique du formalisme Lindblad.

## Fichier machine-readable

Voir [`benchmarks/results/latest.json`](./benchmarks/results/latest.json).
