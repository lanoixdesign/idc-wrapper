"""Agent IDC : ressource finie, journal, règle d'arrêt."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

from .journal import AppendOnlyJournal, JournalEntry


class Backend(Protocol):
    def generate(self, prompt: str, max_tokens: int = 120) -> str: ...


GainFn = Callable[[int, str], float]


def default_gain(step: int, chunk: str) -> float:
    del step
    return 25.0 if len(chunk) > 20 else 8.0


IGNORANCE_MSG = "Je ne sais pas (ressource insuffisante ou incertitude trop élevée)."


@dataclass
class IdcRunResult:
    answer: str
    steps: int
    resource_final: float
    tokens_approx_total: int
    cost_total: float
    stopped_early: bool
    admitted_ignorance: bool
    journal: AppendOnlyJournal
    mode: str  # "idc" | "baseline"


@dataclass
class IdcAgent:
    backend: Backend
    resource: float = 100.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    max_steps: int = 8
    journal: AppendOnlyJournal = field(default_factory=AppendOnlyJournal)
    gain_fn: GainFn = field(default=default_gain)
    use_stop_rule: bool = True
    # Sous IDC : si aucun chunk non vide n'a dépassé le seuil de gain « utile »,
    # préférer l'aveu d'ignorance à une réponse creuse.
    prefer_ignorance_if_no_useful: bool = True
    useful_gain_floor: float = 40.0  # aligné sur cost_per_token*50 par défaut

    def still_worth_it(self, estimated_gain: float) -> bool:
        marginal_cost = self.cost_per_token * 50.0
        risk = 2.0 if self.resource < 30.0 else 1.0
        return estimated_gain > marginal_cost * risk

    def run(self, task: str) -> IdcRunResult:
        current = ""
        step = 0
        tokens_total = 0
        cost_total = 0.0
        stopped_early = False
        max_gain_seen = 0.0
        any_useful = False

        while self.resource > self.critical_threshold and step < self.max_steps:
            step += 1
            context = (
                f"Journal des engagements précédents :\n{self.journal.as_context()}\n\n"
                f"Tâche : {task}\n\n"
                f"Réponse partielle actuelle :\n{current}\n\n"
                "Continue ou affine la réponse. Sois concis."
            )
            chunk = self.backend.generate(context, max_tokens=120)
            tokens_approx = max(len(chunk.split()), 1)  # tentative minimale
            chunk_display = chunk.strip() if chunk.strip() else "(vide / incertitude)"

            cost = tokens_approx * self.cost_per_token
            self.resource = max(0.0, self.resource - cost)
            tokens_total += tokens_approx
            cost_total += cost
            estimated_gain = self.gain_fn(step, chunk)
            max_gain_seen = max(max_gain_seen, estimated_gain)
            if chunk.strip() and estimated_gain >= self.useful_gain_floor:
                any_useful = True

            self.journal.append(
                JournalEntry(
                    step=step,
                    text=chunk_display,
                    resource_after=self.resource,
                    tokens_approx=tokens_approx,
                    cost=cost,
                    estimated_gain=estimated_gain,
                )
            )

            should_stop = False
            if self.use_stop_rule:
                if (not self.still_worth_it(estimated_gain)) or self.resource <= self.critical_threshold:
                    should_stop = True
            else:
                if self.resource <= self.critical_threshold:
                    should_stop = True

            if chunk.strip():
                current = f"{current}{chunk}\n".strip()

            if should_stop:
                break

        if self.use_stop_rule and step < self.max_steps:
            stopped_early = True

        # Politique d'effondrement : ignorance si rien d'utile
        if not current.strip():
            admitted = True
            answer = IGNORANCE_MSG
        elif (
            self.use_stop_rule
            and self.prefer_ignorance_if_no_useful
            and not any_useful
            and max_gain_seen < self.useful_gain_floor
        ):
            admitted = True
            answer = IGNORANCE_MSG
        else:
            admitted = False
            answer = current.strip()

        return IdcRunResult(
            answer=answer,
            steps=step,
            resource_final=self.resource,
            tokens_approx_total=tokens_total,
            cost_total=cost_total,
            stopped_early=stopped_early,
            admitted_ignorance=admitted,
            journal=self.journal,
            mode="idc" if self.use_stop_rule else "baseline",
        )
