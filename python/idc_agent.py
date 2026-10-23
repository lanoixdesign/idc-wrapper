#!/usr/bin/env python3
"""IDC agent loop — portable reference for any OpenAI-compatible chat API.

Usage:
  export OPENAI_API_KEY=...
  # optional: OPENAI_BASE_URL=https://api.openai.com/v1  OPENAI_MODEL=gpt-4o-mini
  python idc_agent.py "Your task here"
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field


@dataclass
class AppendOnlyJournal:
    entries: list[str] = field(default_factory=list)

    def append(self, entry: str) -> None:
        self.entries.append(entry)

    def as_context(self) -> str:
        return "\n---\n".join(self.entries)


@dataclass
class IdcAgent:
    api_url: str
    api_key: str
    model: str
    resource: float = 100.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    max_steps: int = 8
    journal: AppendOnlyJournal = field(default_factory=AppendOnlyJournal)

    def call_model(self, prompt: str, max_tokens: int = 120) -> str:
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        choices = data.get("choices") or []
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content") or ""

    def still_worth_it(self, estimated_gain: float) -> bool:
        marginal_cost = self.cost_per_token * 50.0
        risk = 2.0 if self.resource < 30.0 else 1.0
        return estimated_gain > marginal_cost * risk

    def run(self, task: str) -> str:
        current = ""
        step = 0
        while self.resource > self.critical_threshold and step < self.max_steps:
            step += 1
            context = (
                f"Journal des engagements précédents :\n{self.journal.as_context()}\n\n"
                f"Tâche : {task}\n\n"
                f"Réponse partielle actuelle :\n{current}\n\n"
                "Continue ou affine la réponse. Sois concis."
            )
            try:
                chunk = self.call_model(context, max_tokens=120)
            except urllib.error.HTTPError as e:
                raise SystemExit(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}") from e

            tokens_approx = max(len(chunk.split()), 1)
            cost = tokens_approx * self.cost_per_token
            self.resource = max(0.0, self.resource - cost)
            estimated_gain = 25.0 if len(chunk) > 20 else 8.0

            print(
                f"[étape {step}] R restante = {self.resource:.1f} | "
                f"coût = {cost:.1f} | gain estimé = {estimated_gain:.1f}"
            )

            if (not self.still_worth_it(estimated_gain)) or self.resource <= self.critical_threshold:
                print("→ Arrêt optimal déclenché.")
                if chunk.strip():
                    current = f"{current}{chunk}\n".strip()
                    self.journal.append(f"Étape {step} : {chunk.strip()}")
                break

            current = f"{current}{chunk}\n"
            self.journal.append(f"Étape {step} : {chunk.strip()}")

        if not current.strip():
            return "Je ne sais pas (ressource insuffisante ou incertitude trop élevée)."
        return current.strip()


def main() -> None:
    task = " ".join(sys.argv[1:]).strip() or (
        "Explique en 5 points pourquoi la finitude computationnelle peut réduire les hallucinations."
    )
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    agent = IdcAgent(
        api_url=f"{base}/chat/completions",
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    )
    if not agent.api_key:
        raise SystemExit("Set OPENAI_API_KEY (OpenAI-compatible).")

    result = agent.run(task)
    print("\n=== RÉPONSE FINALE (après effondrement) ===\n" + result)
    print("\n=== JOURNAL APPEND-ONLY ===\n" + agent.journal.as_context())
    print(f"\nRessource finale : {agent.resource:.1f}")


if __name__ == "__main__":
    main()
