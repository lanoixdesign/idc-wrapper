"""IDC — Effondrement Décisionnel Irréversible (Irreversible Decision Collapse).

Package portable (stdlib) pour envelopper un LLM avec ressource finie,
journal append-only et règle d'arrêt.
"""

from .journal import AppendOnlyJournal, JournalEntry
from .agent import IdcAgent, IdcRunResult, Backend
from .mock_backend import MockBackend, MockScenario

__all__ = [
    "AppendOnlyJournal",
    "JournalEntry",
    "IdcAgent",
    "IdcRunResult",
    "Backend",
    "MockBackend",
    "MockScenario",
]

__version__ = "0.2.0"
