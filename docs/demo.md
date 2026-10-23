# Démo — boucle IDC

Flux de décision (mock ou LLM). Aucune perf inventée.

## ASCII

```
  ┌─────────────┐
  │   Tâche     │
  └──────┬──────┘
         ▼
  ┌─────────────┐     R > seuil ?     ┌──────────────┐
  │  Délibérer  │────────────────────▶│  Appel modèle│
  │  (étape n)  │     oui             │  + coût ≈tok │
  └─────────────┘                     └──────┬───────┘
         ▲                                   │
         │                    R -= coût      │
         │                    journal.append │
         │                                   ▼
         │                            ┌─────────────┐
         │         gain > coût×risque │  VOI / stop │
         └────────────────────────────│  rule       │
                     oui              └──────┬──────┘
                                             │ non / R bas
                                             ▼
                                      ┌─────────────┐
                                      │  Collapse   │
                                      │  réponse ou │
                                      │  « je ne    │
                                      │    sais »   │
                                      └─────────────┘
```

## Mermaid

```mermaid
flowchart TD
  A[Tâche] --> B{R > seuil critique<br/>et étapes < max?}
  B -->|non| Z[Collapse: réponse finale<br/>ou « je ne sais pas »]
  B -->|oui| C[Appel modèle / mock]
  C --> D[Coût ≈ tokens × cost_per_token]
  D --> E[R -= coût]
  E --> F[journal.append engagement]
  F --> G{VOI: gain estimé<br/>> coût marginal × risque?}
  G -->|oui| B
  G -->|non| Z
```

## Lancer

```bash
PYTHONPATH=python python3 examples/01_support_client/run_mock.py
PYTHONPATH=python python3 examples/04_langgraph/run_mock.py
```

Voir aussi [PERFORMANCE.md](../PERFORMANCE.md) (chiffres mock uniquement).
