# IDC Wrapper — README (français)

🌐 **Language / Langue** : [English](./README.md) · Français · Protocole : [FR](./docs/PROTOCOL.md) · [EN](./docs/PROTOCOL.en.md)

**Couche d’enveloppe IDC — Effondrement Décisionnel Irréversible** (*Irreversible Decision Collapse*).
Open source (licence MIT), pensée pour tous les runtimes d’agents (Cursor, Claude Code,
LangGraph, OpenAI Agents, boucles custom…). Implémentations Python (référence) et Rust.

## Le concept

Une IA sans **finitude** peut réfléchir sans fin, hésiter, et inventer : inventer ne coûte
souvent pas plus cher qu’avouer « je ne sais pas ». L’IDC enveloppe le modèle avec :

1. une **ressource finie** `R` qui décroît avec le calcul ;
2. un **journal append-only** (engagements irréversibles) ;
3. une **règle d’arrêt VOI** : s’effondrer quand la valeur marginale de réfléchir ne justifie
   plus le coût — halluciner doit coûter plus cher qu’avouer son ignorance.

C’est un **modèle + protocole de test**, pas une preuve empirique déjà validée sur les LLM
de frontier. Les chiffres de performance du dépôt viennent d’un **mock** reproductible —
voir [PERFORMANCE.md](./PERFORMANCE.md).

Paramètres par défaut : `resource` 100.0, `critical_threshold` 15.0, `cost_per_token` 0.8,
`max_steps` 8. Heuristique VOI simple : `estimated_gain > cost_per_token * 50 * risk`.

## Installation

Le paquet est publié sur PyPI sous le nom **`idc-wrapper`** (version 0.2.0 :
<https://pypi.org/project/idc-wrapper/>) :

```bash
pip install idc-wrapper
# extra optionnel LangGraph :
pip install 'idc-wrapper[langgraph]'
```

Depuis un clone du dépôt (installation éditable) :

```bash
pip install -e .
```

Rust : `cargo build --release` (logique dans la crate lib `idc_wrapper`, `src/lib.rs`).

## Utilisation rapide

Exemples repris du [README](./README.md#quickstart-python) :

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

Tests / bench mock (aucune clé) :

```bash
PYTHONPATH=python python3 -m unittest discover -s python/idc -v
PYTHONPATH=python python3 benchmarks/bench_mock.py
```

## Exemples

Cas concrets **Sans IDC / Avec IDC / Bénéfice**, chacun avec un script mock (aucune clé API) —
voir [`examples/README.md`](./examples/README.md) :

| # | Dossier | Idée |
|---|---------|------|
| 01 | [`examples/01_support_client`](./examples/01_support_client/) | Support livraison |
| 02 | [`examples/02_code_assistant`](./examples/02_code_assistant/) | Fix bug + stop avant API fantôme |
| 03 | [`examples/03_research_synth`](./examples/03_research_synth/) | Synthèse bornée, pas de citation inventée |
| 04 | [`examples/04_langgraph`](./examples/04_langgraph/) | Boucle nœud/état style LangGraph + arrêt IDC |
| 05 | [`examples/05_swarm_agents`](./examples/05_swarm_agents/) | Essaim de 4 agents (`R` + journal partagés), toggle `--idc` / `--no-idc` ; mock CI + **mode live Groq** |

Mode live Groq de l’exemple 05 (nécessite la variable d’environnement `GROQ_API_KEY`,
jamais codée en dur) :

```bash
PYTHONPATH=python python3 examples/05_swarm_agents/run_live.py --question "…"
```

Flux ASCII/Mermaid : [`docs/demo.md`](./docs/demo.md). Packs prêts à copier pour Cursor,
Claude Code et OpenAI Agents SDK : [`packs/`](./packs/). Pour les agents : [AGENTS.md](./AGENTS.md).

## Recherche & benchmarks

Le dépôt contient un **protocole pré-enregistré** et un **harness reproductible** sur de
vrais modèles (API Groq) :

- Protocole : [docs/PROTOCOL.md](./docs/PROTOCOL.md) (français, original) ·
  [docs/PROTOCOL.en.md](./docs/PROTOCOL.en.md) (traduction anglaise) — hypothèses
  falsifiables H1–H7, 6 axes de mesure, conditions `sans_idc` / `r_seule` / `voi_seul` /
  `idc` + contrôle `un_appel`, juge aveugle, statistiques (bootstrap par tâche, McNemar).
- Harness : [benchmarks/](./benchmarks/README.md) — 81 tâches versionnées, runner avec
  reprise, juge, analyse → [benchmarks/results/live/REPORT.md](./benchmarks/results/live/REPORT.md).

**État (selon le README au 24/10/2026) : passe pilote partielle seulement**, interrompue par
les quotas gratuits Groq (3 modèles, 1 répétition, conditions `sans_idc` / `idc` / `un_appel` ;
ablations `r_seule` / `voi_seul` pas encore lancées ; une partie des runs pas encore jugée).
Les signaux du pilote **ne permettent pas de conclure** à un gain général de l’IDC. Aucun
claim de performance sur LLM réel n’est fait ici.

## Licence

[MIT](./LICENSE) — Copyright (c) 2026 Micaël Lanoix. Citation : [`CITATION.cff`](./CITATION.cff).

## Contribuer

- Guide : [CONTRIBUTING.md](./CONTRIBUTING.md) (FR + EN)
- Good first issues : [community/GOOD_FIRST_ISSUES.md](./community/GOOD_FIRST_ISSUES.md)
- Conduite : [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · Sécurité : [SECURITY.md](./SECURITY.md) ·
  Roadmap : [ROADMAP.md](./ROADMAP.md)

Contributions bienvenues **avec mesures reproductibles**, pas de chiffres inventés.
