# IDC Wrapper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![CI](https://github.com/lanoixdesign/idc-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/lanoixdesign/idc-wrapper/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./python/)
[![Rust](https://img.shields.io/badge/rust-2021-orange.svg)](./Cargo.toml)

**Couche d’enveloppe IDC — Effondrement Décisionnel Irréversible**  
Open source, pensée pour **tous les runtimes d’agents** (Cursor, Claude Code, LangGraph, OpenAI Agents, boucles custom…).

> **English** — Finite deliberation budget `R`, append-only journal, optimal stop rule.
> Hallucination should cost more than admitting ignorance. Mock benches are real
> numbers on a fake LLM; theory remains hypothesis — see [PERFORMANCE.md](./PERFORMANCE.md).

## Pourquoi l’IDC (vision, sans claims inventés)

Une IA sans **finitude** peut réfléchir sans fin, hésiter, et inventer : inventer
ne coûte souvent pas plus cher qu’avouer « je ne sais pas ». L’IDC propose
d’envelopper le modèle avec :

1. une **ressource finie** `R` qui décroît avec le calcul,
2. un **journal append-only** (engagements irréversibles),
3. une **règle d’arrêt** (s’effondrer quand la valeur marginale de réfléchir
   ne justifie plus le coût).

C’est un **modèle + protocole de test**, pas une preuve empirique déjà validée
sur les LLM de frontier. Les chiffres de ce dépôt viennent d’un **mock**
reproductible — voir [PERFORMANCE.md](./PERFORMANCE.md).

## Table des matières

- [Pour les agents](#pour-les-agents)
- [Quickstart Python](#quickstart-python)
- [Quickstart Rust](#quickstart-rust)
- [Exemples](#exemples)
- [Performance (mock)](#performance-mock)
- [Structure](#structure)
- [Paramètres](#paramètres)
- [Communauté](#communauté)
- [Licence & auteur](#licence--auteur)

## Pour les agents

Lis d’abord **[AGENTS.md](./AGENTS.md)**.

| Fichier | Rôle |
|---------|------|
| [`agents/skills/idc/SKILL.md`](./agents/skills/idc/SKILL.md) | Skill / recipe portable |
| [`schema/idc-protocol.json`](./schema/idc-protocol.json) | Contrat machine-readable |
| [`python/idc/`](./python/idc/) | Package référence (journal, agent, mock) |
| [`python/idc_agent.py`](./python/idc_agent.py) | CLI (OpenAI-compatible ou `--mock`) |
| [`src/main.rs`](./src/main.rs) | Implémentation Rust |
| [`examples/`](./examples/) | Cas Sans IDC / Avec IDC |
| [`PERFORMANCE.md`](./PERFORMANCE.md) | Mesures mock + hypothèses vs démontré |

## Quickstart Python

```bash
# Démo sans clé API (recommandé pour découvrir)
PYTHONPATH=python python3 python/idc_agent.py --mock support_client \
  "Client : où est mon colis ?"

# Comparer baseline (pas de VOI) vs IDC
PYTHONPATH=python python3 python/idc_agent.py --mock verbose --baseline "long"
PYTHONPATH=python python3 python/idc_agent.py --mock verbose "long"

# Avec API compatible OpenAI
export OPENAI_API_KEY=sk-...
# optionnel : OPENAI_BASE_URL=http://localhost:11434/v1  OPENAI_MODEL=llama3.2
PYTHONPATH=python python3 python/idc_agent.py "Explique l’IDC en 5 points"
```

Tests / bench (aucune clé) :

```bash
PYTHONPATH=python python3 -m unittest discover -s python/idc -v
PYTHONPATH=python python3 benchmarks/bench_mock.py
```

## Quickstart Rust

```bash
cargo build --release
export OPENAI_API_KEY=sk-...
./target/release/idc-wrapper
```

Par défaut : `https://api.openai.com/v1/chat/completions`, modèle `gpt-4o-mini`.

## Exemples

Trois cas concrets avec narration **Sans IDC / Avec IDC / Bénéfice** et scripts mock :

| # | Dossier | Idée |
|---|---------|------|
| 01 | [`examples/01_support_client`](./examples/01_support_client/) | Support livraison |
| 02 | [`examples/02_code_assistant`](./examples/02_code_assistant/) | Fix bug + stop avant API fantôme |
| 03 | [`examples/03_research_synth`](./examples/03_research_synth/) | Synthèse bornée, pas de citation inventée |

Voir [`examples/README.md`](./examples/README.md).

## Performance (mock)

Micro-benchmark **Baseline (N fixes) vs IDC (règle d’arrêt)** sur réponses mock.
Dernière agrégation typique (régénérer localement pour confirmer) :

| Agrégat | Baseline | IDC |
|---------|----------|-----|
| Étapes moyennes | 8.0 | ~3.4 |
| Tokens≈ moyens | ~44.8 | ~26.6 |
| R finale moyenne | ~64.2 | ~78.7 |

Détail, caveats, et distinction **hypothèse livre vs démontré par le code** :
**[PERFORMANCE.md](./PERFORMANCE.md)**.

## Structure

```
idc-wrapper/
├── AGENTS.md                 # contrat pour runtimes agents
├── PERFORMANCE.md            # mesures mock honnêtes
├── python/idc/               # package (journal, agent, mock)
├── python/idc_agent.py       # CLI
├── src/main.rs               # Rust
├── schema/idc-protocol.json
├── agents/skills/idc/SKILL.md
├── examples/                 # 3 cas + README
├── benchmarks/               # bench_mock.py + results/
└── .github/                  # CI, templates
```

## Paramètres

| Paramètre | Défaut | Rôle |
|-----------|--------|------|
| `resource` | 100.0 | Budget initial |
| `critical_threshold` | 15.0 | Force l’arrêt |
| `cost_per_token` | 0.8 | Coût approx. par token |
| `max_steps` | 8 | Garde-fou |

Heuristique VOI simple : `estimated_gain > cost_per_token * 50 * risk`.

## Communauté

- Contribuer : [CONTRIBUTING.md](./CONTRIBUTING.md) (FR + EN)
- Conduite : [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- Sécurité : [SECURITY.md](./SECURITY.md)
- Changelog : [CHANGELOG.md](./CHANGELOG.md)
- Issues / PR : templates dans `.github/`

Idées bienvenues : VOI plus fine, persistance disque du journal, crate `lib` Rust,
adapters LangGraph / Agents SDK, calibrage dynamique du seuil — **avec mesures
reproductibles**, pas de chiffres inventés.

## Licence & auteur

[MIT](./LICENSE) — Copyright (c) 2026 Micaël Lanoix

**Micaël Lanoix** — continuité des travaux sur l’ADN numérique des images
(PNGIA / Pixel 4D) et l’Effondrement Décisionnel Irréversible.

Citation : voir [`CITATION.cff`](./CITATION.cff).
