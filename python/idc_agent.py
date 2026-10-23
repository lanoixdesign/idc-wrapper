#!/usr/bin/env python3
"""IDC agent CLI — entrée fine (OpenAI-compatible ou --mock).

Usage:
  export OPENAI_API_KEY=...
  python python/idc_agent.py "Your task here"

  # Sans clé API (démo déterministe) :
  python python/idc_agent.py --mock support_client "Question client : où est mon colis ?"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Permettre `python python/idc_agent.py` depuis la racine du dépôt
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from idc import AppendOnlyJournal, IdcAgent, MockBackend, MockScenario  # noqa: E402
from idc.mock_backend import SCENARIOS  # noqa: E402


class OpenAIBackend:
    def __init__(self, api_url: str, api_key: str, model: str) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 120) -> str:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="IDC agent (OpenAI-compatible or --mock)")
    parser.add_argument("task", nargs="*", help="Tâche / question")
    parser.add_argument(
        "--mock",
        metavar="SCENARIO",
        choices=sorted(SCENARIOS.keys()),
        help="Utiliser un backend mock (pas de clé API)",
    )
    parser.add_argument("--baseline", action="store_true", help="Désactiver la règle d'arrêt VOI")
    parser.add_argument("--resource", type=float, default=100.0)
    parser.add_argument("--threshold", type=float, default=15.0)
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--cost-per-token", type=float, default=0.8)
    args = parser.parse_args()

    task = " ".join(args.task).strip() or (
        "Explique en 5 points pourquoi la finitude computationnelle peut réduire les hallucinations."
    )

    if args.mock:
        scenario = SCENARIOS[args.mock]
        backend: object = MockBackend(scenario=scenario)
        gain_fn = backend.gain_for_step  # type: ignore[attr-defined]
    else:
        base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise SystemExit(
                "Set OPENAI_API_KEY, or pass --mock <scenario> "
                f"(scenarios: {', '.join(sorted(SCENARIOS))})."
            )
        backend = OpenAIBackend(
            api_url=f"{base}/chat/completions",
            api_key=api_key,
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        )
        gain_fn = None

    agent_kwargs = dict(
        backend=backend,
        resource=args.resource,
        critical_threshold=args.threshold,
        cost_per_token=args.cost_per_token,
        max_steps=args.max_steps,
        use_stop_rule=not args.baseline,
    )
    if gain_fn is not None:
        agent_kwargs["gain_fn"] = gain_fn

    agent = IdcAgent(**agent_kwargs)
    try:
        result = agent.run(task)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}") from e

    mode = "BASELINE (pas de VOI)" if args.baseline else "IDC (règle d'arrêt)"
    print(f"=== MODE : {mode} ===")
    for e in result.journal.entries:
        print(
            f"[étape {e.step}] R={e.resource_after:.1f} | "
            f"coût={e.cost:.1f} | gain≈{e.estimated_gain:.1f} | tokens≈{e.tokens_approx}"
        )
    if result.stopped_early:
        print("→ Arrêt anticipé (VOI / seuil).")
    print("\n=== RÉPONSE FINALE (après effondrement) ===\n" + result.answer)
    print("\n=== JOURNAL APPEND-ONLY ===\n" + result.journal.as_context())
    print(
        f"\nRessource finale : {result.resource_final:.1f} | "
        f"étapes : {result.steps} | tokens≈{result.tokens_approx_total} | "
        f"ignorance : {result.admitted_ignorance}"
    )


# Ré-exports pour import legacy : `from idc_agent import IdcAgent, AppendOnlyJournal`
__all__ = ["AppendOnlyJournal", "IdcAgent", "MockBackend", "MockScenario", "main"]

if __name__ == "__main__":
    main()
