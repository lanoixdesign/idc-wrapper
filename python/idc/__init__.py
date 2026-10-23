"""IDC — Effondrement Décisionnel Irréversible (Irreversible Decision Collapse).

Package portable (stdlib) pour envelopper un LLM avec ressource finie,
journal append-only et règle d'arrêt. Backend Groq optionnel via
``GROQ_API_KEY`` (``idc.groq_backend``).

L'adaptateur LangGraph-shaped vit dans `idc.langgraph_adapter` (pas d'import
lourd ici) : `IdcGraphRunner` fonctionne sans langgraph ;
`compile_langgraph` requiert l'extra optionnel `[langgraph]`.
"""

from .journal import AppendOnlyJournal, JournalEntry
from .agent import IdcAgent, IdcRunResult, Backend
from .mock_backend import MockBackend, MockScenario
from .groq_backend import GroqBackend, DEFAULT_GROQ_MODEL

__all__ = [
    "AppendOnlyJournal",
    "JournalEntry",
    "IdcAgent",
    "IdcRunResult",
    "Backend",
    "MockBackend",
    "MockScenario",
    "GroqBackend",
    "DEFAULT_GROQ_MODEL",
]

__version__ = "0.2.0"
