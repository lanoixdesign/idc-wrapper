"""Illustration OpenAI Agents + IDC — non importé par le package idc."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IdcSession:
    resource: float = 100.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    journal: list[str] = field(default_factory=list)

    def append(self, entry: str) -> None:
        self.journal.append(entry)

    def should_continue(self, estimated_gain: float) -> bool:
        if self.resource <= self.critical_threshold:
            return False
        risk = 2.0 if self.resource < 30.0 else 1.0
        return estimated_gain > self.cost_per_token * 50.0 * risk

    def charge(self, tokens_approx: float) -> None:
        self.resource = max(0.0, self.resource - tokens_approx * self.cost_per_token)


def wrap_agent_with_idc(agent, session: IdcSession | None = None):
    session = session or IdcSession()
    raise NotImplementedError(
        "Adapter OpenAI Agents SDK non livré (roadmap v0.4). "
        "Utilise python/idc/agent.py ou langgraph_adapter.py en attendant."
    )
