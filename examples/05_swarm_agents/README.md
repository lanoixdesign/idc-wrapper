# 05 — Essaim d'agents (incident support)

Scénario concret : **4 agents spécialisés** synthétisent une réponse client
après une panne API paiement.

| Rôle | Mission |
|------|---------|
| chercheur | Collecte les faits (périmètre, durée, tickets) |
| critique | Borne les affirmations trop larges |
| rédacteur | Produit la réponse client actionnable |
| coordonnateur | Orchestre / relance l'essaim |

## Choix pédagogique : pool partagé

- **Une seule ressource `R`** pour tout l'essaim (chaque tour d'un rôle
  consomme le même budget).
- **Un journal append-only partagé** : chaque engagement d'un agent est
  visible des suivants (pas de réécriture).

Alternative possible (non utilisée ici) : `R` par agent — plus réaliste pour
des quotas séparés, moins lisible pour montrer l'arrêt collectif.

## Sans IDC

Les agents **se renvoient la balle** jusqu'à `max_rounds` : reformulations,
SLA inventé, faux CVE, post-mortem fantôme. Plus d'étapes, plus de tokens,
réponse **bruyante**.

## Avec IDC

Après les tours utiles (faits → critique → brouillon), la **règle d'arrêt
(VOI)** coupe la boucle : le gain marginal de la relance du coordonnateur
ne justifie plus le coût. Hallucinations du scénario mock **non atteintes**.

## Bénéfice

Moins d'étapes, `R` finale plus haute, réponse limitée aux engagements utiles
du journal partagé.

## Lancer

```bash
# depuis la racine du dépôt — les deux modes (défaut, comparable)
PYTHONPATH=python python examples/05_swarm_agents/run_mock.py

# un seul mode
PYTHONPATH=python python examples/05_swarm_agents/run_mock.py --idc
PYTHONPATH=python python examples/05_swarm_agents/run_mock.py --no-idc

# via env (équivalent)
IDC=1 PYTHONPATH=python python examples/05_swarm_agents/run_mock.py
IDC=0 PYTHONPATH=python python examples/05_swarm_agents/run_mock.py
```

Aucune clé API, aucun réseau. Attendu typique (mock déterministe) :

| Mode | Étapes | Comportement |
|------|--------|--------------|
| `--no-idc` | ~8–12 | ping-pong + SLA/CVE inventés, `R` basse |
| `--idc` | ~4 | arrêt après synthèse utile, `R` préservée |

> **English** — Deterministic mock swarm demo (shared R + shared journal).
> Not a production multi-agent benchmark. See [PERFORMANCE.md](../../PERFORMANCE.md).
