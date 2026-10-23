#!/usr/bin/env python3
"""Régénère PERFORMANCE.md à partir de benchmarks/results/latest.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks" / "results" / "latest.json"
OUT = ROOT / "PERFORMANCE.md"


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    rows = d["rows"]
    agg = d["aggregates"]
    meta = d["meta"]

    def cell(v: object) -> str:
        if isinstance(v, float):
            return f"{v:.1f}" if abs(v) >= 1 else f"{v:.3f}"
        if isinstance(v, bool):
            return "oui" if v else "non"
        return str(v)

    table_lines = [
        "| Scénario | Mode | Étapes | Tokens≈ | R finale | Coût | Arrêt anticipé | Ignorance |",
        "|----------|------|--------|---------|----------|------|----------------|-----------|",
    ]
    for r in rows:
        table_lines.append(
            f"| {r['scenario']} | {r['mode']} | {r['steps']} | {r['tokens_approx']} | "
            f"{r['resource_final']:.1f} | {r['cost_total']:.1f} | "
            f"{cell(r['stopped_early'])} | {cell(r['admitted_ignorance'])} |"
        )
    table = "\n".join(table_lines)

    # Convert generated_at UTC to Europe/Warsaw display hint
    gen = meta.get("generated_at", "?")

    md = f"""# PERFORMANCE — mesures mock reproductibles

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
| Généré (UTC) | `{gen}` |
| Python | {meta.get("python")} |
| Plateforme | {meta.get("platform")} |
| Version IDC packagée | {meta.get("idc_version")} |

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

{table}

### Agrégats

| Agrégat | Baseline | IDC |
|---------|----------|-----|
| Étapes moyennes | {agg['avg_steps_baseline']} | {agg['avg_steps_idc']} |
| Tokens≈ moyens | {agg['avg_tokens_baseline']} | {agg['avg_tokens_idc']} |
| R finale moyenne | {agg['avg_resource_final_baseline']} | {agg['avg_resource_final_idc']} |
| Taux ignorance (`uncertain`, {agg['uncertain_budget_variants']} budgets) | {agg['forced_ignorance_rate_uncertain_baseline']} | {agg['forced_ignorance_rate_uncertain_idc']} |

Lecture honnête sur ce mock :

- **IDC coupe la boucle** : ~{agg['avg_steps_idc']} étapes vs {agg['avg_steps_baseline']} en baseline ; les étapes « hallucination / digression » des scénarios ne sont pas atteintes.
- **Ressource préservée** : R finale moyenne plus haute sous IDC ({agg['avg_resource_final_idc']} vs {agg['avg_resource_final_baseline']}).
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
"""
    OUT.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
