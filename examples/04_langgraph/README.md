# 04 — Adaptateur LangGraph-shaped

Montre comment envelopper une boucle **nœud / état** (style LangGraph) avec
la ressource finie IDC, le journal append-only et la règle d'arrêt.

## Sans installer langgraph (recommandé pour la démo)

```bash
# depuis la racine du dépôt
PYTHONPATH=python python3 examples/04_langgraph/run_mock.py
```

Le script utilise `IdcGraphRunner` : même modèle mental qu'un `StateGraph`
(`deliberation_node` + `should_continue`), **stdlib uniquement** + mock.

Attendu typique sur le scénario `verbose` :
- Baseline : ~8 étapes
- IDC : arrêt anticipé (~3–4 étapes), `R` finale plus haute

## Avec langgraph réel (optionnel)

```bash
pip install 'idc-wrapper[langgraph]'
# ou : pip install langgraph
```

```python
from idc import MockBackend
from idc.mock_backend import VERBOSE
from idc.langgraph_adapter import compile_langgraph, initial_state

b = MockBackend(VERBOSE)
graph = compile_langgraph(backend=b, use_stop_rule=True, gain_fn=b.gain_for_step)
out = graph.invoke(initial_state("ma tâche", use_stop_rule=True))
print(out["answer"], out["step"], out["resource"])
```

Si `langgraph` est absent, `compile_langgraph()` / `require_langgraph()`
lèvent un `ImportError` avec le hint d'installation — le runner stdlib reste
disponible.

> **English** — Mock demo only. No invented LLM performance claims.
> See [PERFORMANCE.md](../../PERFORMANCE.md).
