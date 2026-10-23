# IDC Wrapper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Release](https://img.shields.io/github/v/release/lanoixdesign/idc-wrapper?display_name=tag&sort=semver)](https://github.com/lanoixdesign/idc-wrapper/releases/tag/v0.2.0)
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

## Livre / concept

- Livre (Amazon FR) : [Effondrement Décisionnel Irréversible](https://www.amazon.fr/dp/B0HMX1CY6R)
- Citation machine-readable : [`CITATION.cff`](./CITATION.cff)

## Table des matières

- [Pour les agents](#pour-les-agents)
- [Quickstart Python](#quickstart-python)
- [Quickstart Rust](#quickstart-rust)
- [Exemples](#exemples)
- [Adaptateur LangGraph](#adaptateur-langgraph)
- [Packs agents](#packs-agents)
- [Performance (mock)](#performance-mock)
- [Structure](#structure)
- [Paramètres](#paramètres)
- [Roadmap](#roadmap)
- [Communauté](#communauté)
- [Licence & auteur](#licence--auteur)

## Pour les agents

Lis d’abord **[AGENTS.md](./AGENTS.md)**.

| Fichier | Rôle |
|---------|------|
| [`agents/skills/idc/SKILL.md`](./agents/skills/idc/SKILL.md) | Skill / recipe portable |
| [`schema/idc-protocol.json`](./schema/idc-protocol.json) | Contrat machine-readable |
| [`python/idc/`](./python/idc/) | Package référence (journal, agent, mock) |
| [`python/idc/langgraph_adapter.py`](./python/idc/langgraph_adapter.py) | Adaptateur LangGraph-shaped (optionnel) |
| [`python/idc_agent.py`](./python/idc_agent.py) | CLI (OpenAI-compatible ou `--mock`) |
| [`src/lib.rs`](./src/lib.rs) | Bibliothèque Rust (`IdcAgent`, journal) |
| [`src/main.rs`](./src/main.rs) | Binaire CLI mince |
| [`examples/`](./examples/) | Cas Sans IDC / Avec IDC |
| [`packs/`](./packs/) | Snippets Cursor / Claude / OpenAI Agents |
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

Installation package (editable locale ; PyPI public prévu — voir [PUBLISHING.md](./PUBLISHING.md)) :

```bash
pip install -e .
# ou plus tard : pip install idc-wrapper
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

La logique vit dans la **crate lib** `idc_wrapper` (`src/lib.rs`) ; le binaire
`src/main.rs` l’appelle seulement. Par défaut : `https://api.openai.com/v1/chat/completions`,
modèle `gpt-4o-mini`.

> **Note toolchain** : `cargo check` / `cargo build` nécessitent un Rust stable
> récent (CI utilise `dtolnay/rust-toolchain@stable`). Si ton `rustc` local est
> trop ancien pour les dépendances (`reqwest` / `tokio`), la structure lib+bin
> reste valide — mets à jour le toolchain ou peaufine en CI.

## Exemples

Cas concrets avec narration **Sans IDC / Avec IDC / Bénéfice** et scripts mock :

| # | Dossier | Idée |
|---|---------|------|
| 01 | [`examples/01_support_client`](./examples/01_support_client/) | Support livraison |
| 02 | [`examples/02_code_assistant`](./examples/02_code_assistant/) | Fix bug + stop avant API fantôme |
| 03 | [`examples/03_research_synth`](./examples/03_research_synth/) | Synthèse bornée, pas de citation inventée |
| 04 | [`examples/04_langgraph`](./examples/04_langgraph/) | Boucle nœud/état style LangGraph + arrêt IDC |
| 05 | [`examples/05_swarm_agents`](./examples/05_swarm_agents/) | Essaim multi-agents, toggle `--idc` / `--no-idc` |

Voir [`examples/README.md`](./examples/README.md). Flux ASCII/Mermaid : [`docs/demo.md`](./docs/demo.md).

## Adaptateur LangGraph

Boucle **nœud / état** compatible LangGraph, **sans dépendance obligatoire** :

```bash
# démo mock (stdlib)
PYTHONPATH=python python3 examples/04_langgraph/run_mock.py

# optionnel : vrai StateGraph
pip install 'idc-wrapper[langgraph]'   # ou : pip install langgraph
```

```python
from idc.langgraph_adapter import IdcGraphRunner, compile_langgraph
# IdcGraphRunner : toujours disponible
# compile_langgraph(...) : ImportError clair si langgraph absent
```

Détails : [`examples/04_langgraph/README.md`](./examples/04_langgraph/README.md).

## Packs agents

Snippets copy-paste prêts :

| Runtime | Pack |
|---------|------|
| Cursor | [`packs/cursor/RULE.md`](./packs/cursor/RULE.md) + [`packs/cursor/idc.mdc`](./packs/cursor/idc.mdc) |
| Claude Code | [`packs/claude/CLAUDE.md`](./packs/claude/CLAUDE.md) |
| OpenAI Agents SDK | [`packs/openai-agents/README.md`](./packs/openai-agents/README.md) (interface + stub) |

## Performance (mock)

Micro-benchmark **Baseline (N fixes) vs IDC (règle d’arrêt)** sur réponses mock.
Dernière agrégation typique (régénérer localement pour confirmer) :

| Agrégat | Baseline | IDC |
|---------|----------|-----|
| Étapes moyennes | 8.0 | ~3.4 |
| Tokens≈ moyens | ~44.8 | ~26.6 |
| R finale moyenne | ~64.2 | ~78.7 |

Détail, caveats, et distinction **hypothèse livre vs démontré par le code** :
**[PERFORMANCE.md](./PERFORMANCE.md)**. Aucun claim de perf LLM réel ici.

## Structure

```
idc-wrapper/
├── AGENTS.md                 # contrat pour runtimes agents
├── PERFORMANCE.md            # mesures mock honnêtes
├── ROADMAP.md                # v0.3 / v0.4
├── PUBLISHING.md             # PyPI trusted publisher
├── python/idc/               # package (journal, agent, mock, langgraph_adapter)
├── python/idc_agent.py       # CLI
├── src/lib.rs                # crate Rust publique
├── src/main.rs               # binaire mince
├── schema/idc-protocol.json
├── agents/skills/idc/SKILL.md
├── packs/                    # Cursor / Claude / OpenAI Agents
├── examples/                 # 4 cas + README (dont LangGraph)
├── docs/demo.md              # flux IDC (ASCII / Mermaid)
├── benchmarks/               # bench_mock.py + results/
├── community/                # good-first-issues prêts à coller
└── .github/                  # CI, publish-pypi, templates
```

## Paramètres

| Paramètre | Défaut | Rôle |
|-----------|--------|------|
| `resource` | 100.0 | Budget initial |
| `critical_threshold` | 15.0 | Force l’arrêt |
| `cost_per_token` | 0.8 | Coût approx. par token |
| `max_steps` | 8 | Garde-fou |

Heuristique VOI simple : `estimated_gain > cost_per_token * 50 * risk`.

## Roadmap

Priorités v0.3 / v0.4 (PyPI live, crates.io, bench LLM réel, plus d’adapters) :
**[ROADMAP.md](./ROADMAP.md)**.

## Communauté

- Contribuer : [CONTRIBUTING.md](./CONTRIBUTING.md) (FR + EN) — active aussi **Discussions** (Settings → Features)
- Conduite : [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- Sécurité : [SECURITY.md](./SECURITY.md)
- Changelog : [CHANGELOG.md](./CHANGELOG.md)
- Good first issues : [community/GOOD_FIRST_ISSUES.md](./community/GOOD_FIRST_ISSUES.md)
- Issues / PR : templates dans `.github/`
- Publication PyPI : [PUBLISHING.md](./PUBLISHING.md)

Idées bienvenues : VOI plus fine, persistance disque du journal, publish crates.io,
adapter Agents SDK réel, calibrage dynamique du seuil — **avec mesures
reproductibles**, pas de chiffres inventés. (Adaptateur LangGraph-shaped : v0.2.0.)

## Licence & auteur

[MIT](./LICENSE) — Copyright (c) 2026 Micaël Lanoix

**Micaël Lanoix** — continuité des travaux sur l’ADN numérique des images
(PNGIA / Pixel 4D) et l’Effondrement Décisionnel Irréversible.

Citation : voir [`CITATION.cff`](./CITATION.cff). Livre : [Amazon FR](https://www.amazon.fr/dp/B0HMX1CY6R).
