"""Journal append-only : engagements irréversibles."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class JournalEntry:
    step: int
    text: str
    resource_after: float
    tokens_approx: int = 0
    cost: float = 0.0
    estimated_gain: float = 0.0


@dataclass
class AppendOnlyJournal:
    """Liste d'engagements ; on ne peut qu'ajouter (jamais réécrire)."""

    entries: list[JournalEntry] = field(default_factory=list)

    def append(self, entry: JournalEntry) -> None:
        self.entries.append(entry)

    def as_context(self) -> str:
        if not self.entries:
            return "(vide)"
        return "\n---\n".join(
            f"Étape {e.step} (R={e.resource_after:.1f}) : {e.text}" for e in self.entries
        )

    def to_dicts(self) -> list[dict]:
        return [
            {
                "step": e.step,
                "text": e.text,
                "resource_after": e.resource_after,
                "tokens_approx": e.tokens_approx,
                "cost": e.cost,
                "estimated_gain": e.estimated_gain,
            }
            for e in self.entries
        ]

    def __len__(self) -> int:
        return len(self.entries)
