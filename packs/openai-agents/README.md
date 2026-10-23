# Pack OpenAI Agents SDK — interface + stub

**Statut** : guidance + stub. **Pas** de dépendance `openai-agents` déclarée
dans `pyproject.toml` tant que l’adapter n’est pas implémenté et testé.
Ne `pip install` rien d’obligatoire pour lire ce pack.

## Idée

Envelopper un agent OpenAI Agents SDK avec la même boucle IDC que
`python/idc/agent.py` : ressource `R`, journal append-only, règle d’arrêt.

## Interface cible (stable)

```python
from typing import Protocol, Any

class IdcOpenAIAgentsBridge(Protocol):
    """Contrat minimal — à implémenter quand le SDK est une dep optionnelle."""

    def wrap(self, agent: Any) -> Any:
        """Retourne un agent dont `run` respecte IDC (R, journal, stop)."""
        ...

    def journal(self) -> list[str]:
        """Engagements append-only depuis le début de la session."""
        ...
```

## Stub (copy-paste)

```python
# packs/openai-agents/stub.py — illustration, non importé par le package
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IdcSession:
    resource: float = 100.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    journal: list[str] = field(default_factory=list)

    def append(self, entry: str) -> None:
        self.journal.append(entry)  # append-only

    def should_continue(self, estimated_gain: float) -> bool:
        if self.resource <= self.critical_threshold:
            return False
        risk = 2.0 if self.resource < 30.0 else 1.0
        return estimated_gain > self.cost_per_token * 50.0 * risk

    def charge(self, tokens_approx: float) -> None:
        self.resource = max(0.0, self.resource - tokens_approx * self.cost_per_token)


def wrap_agent_with_idc(agent, session: IdcSession | None = None):
    """
    Placeholder : brancher ici le hook pre/post du SDK OpenAI Agents.
    Aujourd'hui : utilise plutôt IdcAgent / IdcGraphRunner côté python/idc/.
    """
    session = session or IdcSession()
    raise NotImplementedError(
        "Adapter OpenAI Agents SDK non livré (roadmap v0.4). "
        "Utilise python/idc/agent.py ou langgraph_adapter.py en attendant."
    )
```

## En attendant v0.4

| Besoin | Utiliser |
|--------|----------|
| Boucle IDC stdlib | `from idc import IdcAgent` / `python/idc_agent.py` |
| Style graphe | `idc.langgraph_adapter.IdcGraphRunner` |
| Contrat machine | `schema/idc-protocol.json` |

PR bienvenue pour un vrai adapter derrière extra optionnel
`pip install idc-wrapper[openai-agents]` — avec tests mock, sans clé obligatoire.
