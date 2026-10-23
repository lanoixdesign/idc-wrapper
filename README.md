# IDC Wrapper

**Couche d’enveloppe IDC (Effondrement Décisionnel Irréversible)** — open source, pensée pour **tous les agents**.

Ce dépôt impose autour d’un LLM (API compatible OpenAI) :

- une **ressource finie** `R` qui décroît avec le calcul,
- un **journal append-only** (engagements irréversibles),
- une **règle d’arrêt** (on s’arrête quand la valeur marginale de réfléchir ne justifie plus le coût).

L’objectif : forcer une finitude computationnelle pour des décisions plus nettes, moins coûteuses, et rendre l’hallucination moins attractive que l’aveu d’ignorance.

## Pour les agents (Cursor, Claude Code, LangGraph, …)

Lis d’abord **[AGENTS.md](./AGENTS.md)**.

| Fichier | Rôle |
|---------|------|
| [`agents/skills/idc/SKILL.md`](./agents/skills/idc/SKILL.md) | Skill / recipe portable |
| [`schema/idc-protocol.json`](./schema/idc-protocol.json) | Contrat machine-readable |
| [`python/idc_agent.py`](./python/idc_agent.py) | Boucle de référence (stdlib) |
| [`src/main.rs`](./src/main.rs) | Implémentation Rust |

## Concept

L’IDC ne remplace pas le modèle. Il l’enveloppe :

1. Initialiser une ressource `R` (ex. 100).
2. À chaque étape : appeler le LLM, consommer de la ressource, juger si continuer vaut le coup.
3. Quand `R` approche le seuil critique ou que le gain marginal est faible → **effondrement** (réponse engagée).
4. Tout est consignué dans un journal irréversible.

## Prérequis

- Clé API compatible OpenAI : `OPENAI_API_KEY`
- Optionnel : `OPENAI_BASE_URL`, `OPENAI_MODEL` (Python)
- Rust 2021 **ou** Python 3.10+

## Rust

```bash
cargo build --release
export OPENAI_API_KEY=sk-...
./target/release/idc-wrapper
```

Par défaut : `https://api.openai.com/v1/chat/completions`, modèle `gpt-4o-mini`.

## Python (portable)

```bash
export OPENAI_API_KEY=sk-...
# optionnel pour Ollama / vLLM :
# export OPENAI_BASE_URL=http://localhost:11434/v1
# export OPENAI_MODEL=llama3.2
python python/idc_agent.py "Explique l’IDC en 5 points"
```

### Paramètres (défauts)

| Paramètre | Défaut | Rôle |
|-----------|--------|------|
| `resource` | 100.0 | Budget initial |
| `critical_threshold` / `seuil_critique` | 15.0 | Force l’arrêt |
| `cost_per_token` / `cout_par_token` | 0.8 | Coût approx. par token |
| `max_steps` | 8 | Garde-fou |

## Structure

- `AppendOnlyJournal` — journal irréversible
- `IdcAgent` — ressource, appels modèle, décision d’arrêt
- heuristique VOI simple (`still_worth_it` / `vaut_encore_la_peine`)
- `run` — boucle d’effondrement

## Améliorations possibles

- VOI plus fine (entropie, petit modèle secondaire)
- Persistance disque du journal
- Crate `lib` Rust pour embedding
- Adapters LangGraph / OpenAI Agents SDK
- Calibrage dynamique du seuil

## Licence

[MIT](./LICENSE) — Copyright (c) 2026 Micaël Lanoix

## Auteur

Micaël Lanoix — continuité des travaux sur l’ADN numérique des images (PNGIA / Pixel 4D) et l’Effondrement Décisionnel Irréversible.
