# Exemples IDC

Quatre cas concrets **Sans IDC / Avec IDC**, chacun avec un script mock exécutable
(aucune clé API).

| # | Dossier | Scénario |
|---|---------|----------|
| 01 | [`01_support_client`](./01_support_client/) | Support client / livraison |
| 02 | [`02_code_assistant`](./02_code_assistant/) | Assistant code / bug |
| 03 | [`03_research_synth`](./03_research_synth/) | Synthèse de recherche |
| 04 | [`04_langgraph`](./04_langgraph/) | Adaptateur LangGraph-shaped |

## Lancer tous les exemples

```bash
# depuis la racine du dépôt
python examples/01_support_client/run_mock.py
python examples/02_code_assistant/run_mock.py
python examples/03_research_synth/run_mock.py
python examples/04_langgraph/run_mock.py
```

Chaque script affiche côte à côte : croissance du journal, décroissance de `R`,
arrêt anticipé (IDC) vs boucle jusqu'à `max_steps` (baseline).

> **English** — These are deterministic mock demos, not production LLM benchmarks.
> See [PERFORMANCE.md](../PERFORMANCE.md) for measured mock metrics and caveats.
