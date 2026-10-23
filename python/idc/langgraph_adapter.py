"""Adaptateur LangGraph-shaped pour IDC (dépendance optionnelle).

Ce module **ne requiert pas** `langgraph` pour fonctionner : il expose une
boucle nœud/état compatible avec le modèle mental de LangGraph (state dict,
nœud de délibération, condition d'arrêt). Si `langgraph` est installé
(`pip install idc-wrapper[langgraph]`), `compile_langgraph()` construit un
vrai `StateGraph` ; sinon un ImportError clair est levé uniquement pour
cette voie.

Usage minimal (sans langgraph) ::

    from idc.langgraph_adapter import IdcGraphRunner
    from idc import MockBackend
    from idc.mock_backend import VERBOSE

    runner = IdcGraphRunner(backend=MockBackend(VERBOSE), use_stop_rule=True)
    result = runner.run("tâche")

Usage LangGraph réel (si installé) ::

    from idc.langgraph_adapter import compile_langgraph
    graph = compile_langgraph(backend=..., use_stop_rule=True)
    out = graph.invoke({"task": "...", "resource": 100.0, ...})
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, MutableMapping, Optional, Protocol

from .agent import Backend, GainFn, IGNORANCE_MSG, IdcRunResult, default_gain
from .journal import AppendOnlyJournal, JournalEntry


LANGGRAPH_INSTALL_HINT = (
    "langgraph n'est pas installé. "
    "Installez l'extra optionnel : pip install 'idc-wrapper[langgraph]' "
    "ou pip install langgraph. "
    "Sinon utilisez IdcGraphRunner (même interface nœud/état, sans dépendance)."
)


class _LangGraphMissing(Protocol):
    """Marqueur de typage uniquement."""


def require_langgraph() -> Any:
    """Importe langgraph ou lève ImportError avec message d'installation."""
    try:
        import langgraph  # noqa: F401
        from langgraph.graph import END, StateGraph  # type: ignore

        return StateGraph, END
    except ImportError as exc:  # pragma: no cover - chemin optionnel
        raise ImportError(LANGGRAPH_INSTALL_HINT) from exc


# ---------------------------------------------------------------------------
# État LangGraph-shaped (stdlib)
# ---------------------------------------------------------------------------

IdcState = dict[str, Any]
# Clés attendues :
#   task: str
#   answer: str
#   partial: str
#   step: int
#   resource: float
#   tokens_approx_total: int
#   cost_total: float
#   stopped: bool
#   admitted_ignorance: bool
#   journal_entries: list[dict]
#   last_chunk: str
#   last_gain: float
#   max_gain_seen: float
#   any_useful: bool
#   use_stop_rule: bool


def initial_state(
    task: str,
    *,
    resource: float = 100.0,
    use_stop_rule: bool = True,
) -> IdcState:
    return {
        "task": task,
        "answer": "",
        "partial": "",
        "step": 0,
        "resource": float(resource),
        "tokens_approx_total": 0,
        "cost_total": 0.0,
        "stopped": False,
        "admitted_ignorance": False,
        "journal_entries": [],
        "last_chunk": "",
        "last_gain": 0.0,
        "max_gain_seen": 0.0,
        "any_useful": False,
        "use_stop_rule": use_stop_rule,
    }


@dataclass
class IdcGraphConfig:
    """Paramètres partagés par le nœud de délibération et le runner."""

    backend: Backend
    resource_init: float = 100.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    max_steps: int = 8
    gain_fn: GainFn = field(default=default_gain)
    use_stop_rule: bool = True
    prefer_ignorance_if_no_useful: bool = True
    useful_gain_floor: float = 40.0

    def still_worth_it(self, estimated_gain: float, resource: float) -> bool:
        marginal_cost = self.cost_per_token * 50.0
        risk = 2.0 if resource < 30.0 else 1.0
        return estimated_gain > marginal_cost * risk


def deliberation_node(state: Mapping[str, Any], cfg: IdcGraphConfig) -> IdcState:
    """Un tour de délibération IDC (nœud LangGraph-shaped).

    Met à jour ressource, journal, gain ; marque `stopped` si la règle
    d'arrêt (ou le seuil critique / max_steps) l'exige.
    """
    s = dict(state)
    if s.get("stopped"):
        return s

    step = int(s.get("step", 0)) + 1
    resource = float(s.get("resource", cfg.resource_init))
    partial = str(s.get("partial", ""))
    task = str(s.get("task", ""))
    journal_entries = list(s.get("journal_entries") or [])

    context = (
        f"Journal des engagements précédents :\n"
        f"{_journal_as_context(journal_entries)}\n\n"
        f"Tâche : {task}\n\n"
        f"Réponse partielle actuelle :\n{partial}\n\n"
        "Continue ou affine la réponse. Sois concis."
    )
    chunk = cfg.backend.generate(context, max_tokens=120)
    tokens_approx = max(len(chunk.split()), 1)
    chunk_display = chunk.strip() if chunk.strip() else "(vide / incertitude)"
    cost = tokens_approx * cfg.cost_per_token
    resource = max(0.0, resource - cost)
    estimated_gain = cfg.gain_fn(step, chunk)

    journal_entries.append(
        {
            "step": step,
            "text": chunk_display,
            "resource_after": resource,
            "tokens_approx": tokens_approx,
            "cost": cost,
            "estimated_gain": estimated_gain,
        }
    )

    max_gain_seen = max(float(s.get("max_gain_seen", 0.0)), estimated_gain)
    any_useful = bool(s.get("any_useful", False))
    if chunk.strip() and estimated_gain >= cfg.useful_gain_floor:
        any_useful = True

    use_stop = bool(s.get("use_stop_rule", cfg.use_stop_rule))
    should_stop = False
    if use_stop:
        if (not cfg.still_worth_it(estimated_gain, resource)) or resource <= cfg.critical_threshold:
            should_stop = True
    else:
        if resource <= cfg.critical_threshold:
            should_stop = True
    if step >= cfg.max_steps:
        should_stop = True

    if chunk.strip():
        partial = f"{partial}{chunk}\n".strip()

    s.update(
        {
            "step": step,
            "resource": resource,
            "tokens_approx_total": int(s.get("tokens_approx_total", 0)) + tokens_approx,
            "cost_total": float(s.get("cost_total", 0.0)) + cost,
            "journal_entries": journal_entries,
            "last_chunk": chunk_display,
            "last_gain": estimated_gain,
            "max_gain_seen": max_gain_seen,
            "any_useful": any_useful,
            "partial": partial,
            "stopped": should_stop,
            "use_stop_rule": use_stop,
        }
    )
    if should_stop:
        s.update(_finalize(s, cfg))
    return s


def should_continue(state: Mapping[str, Any]) -> str:
    """Condition de routage : ``continue`` | ``end``."""
    return "end" if state.get("stopped") else "continue"


def _finalize(state: Mapping[str, Any], cfg: IdcGraphConfig) -> dict[str, Any]:
    partial = str(state.get("partial", "")).strip()
    use_stop = bool(state.get("use_stop_rule", cfg.use_stop_rule))
    any_useful = bool(state.get("any_useful", False))
    max_gain_seen = float(state.get("max_gain_seen", 0.0))

    if not partial:
        return {"answer": IGNORANCE_MSG, "admitted_ignorance": True}
    if (
        use_stop
        and cfg.prefer_ignorance_if_no_useful
        and not any_useful
        and max_gain_seen < cfg.useful_gain_floor
    ):
        return {"answer": IGNORANCE_MSG, "admitted_ignorance": True}
    return {"answer": partial, "admitted_ignorance": False}


def _journal_as_context(entries: list[dict]) -> str:
    if not entries:
        return "(vide)"
    return "\n---\n".join(
        f"Étape {e['step']} (R={e['resource_after']:.1f}) : {e['text']}" for e in entries
    )


def state_to_result(state: Mapping[str, Any], cfg: IdcGraphConfig) -> IdcRunResult:
    """Convertit l'état final en `IdcRunResult` (compat IdcAgent)."""
    journal = AppendOnlyJournal()
    for e in state.get("journal_entries") or []:
        journal.append(
            JournalEntry(
                step=int(e["step"]),
                text=str(e["text"]),
                resource_after=float(e["resource_after"]),
                tokens_approx=int(e.get("tokens_approx", 0)),
                cost=float(e.get("cost", 0.0)),
                estimated_gain=float(e.get("estimated_gain", 0.0)),
            )
        )
    use_stop = bool(state.get("use_stop_rule", cfg.use_stop_rule))
    step = int(state.get("step", 0))
    stopped_early = bool(use_stop and step < cfg.max_steps and state.get("stopped"))
    return IdcRunResult(
        answer=str(state.get("answer", "")),
        steps=step,
        resource_final=float(state.get("resource", 0.0)),
        tokens_approx_total=int(state.get("tokens_approx_total", 0)),
        cost_total=float(state.get("cost_total", 0.0)),
        stopped_early=stopped_early,
        admitted_ignorance=bool(state.get("admitted_ignorance", False)),
        journal=journal,
        mode="idc" if use_stop else "baseline",
    )


@dataclass
class IdcGraphRunner:
    """Boucle nœud/état IDC sans dépendance langgraph.

    Miroir conceptuel d'un StateGraph à un nœud ``deliberate`` + arête
    conditionnelle ``should_continue``.
    """

    backend: Backend
    resource: float = 100.0
    critical_threshold: float = 15.0
    cost_per_token: float = 0.8
    max_steps: int = 8
    gain_fn: GainFn = field(default=default_gain)
    use_stop_rule: bool = True
    prefer_ignorance_if_no_useful: bool = True
    useful_gain_floor: float = 40.0

    def config(self) -> IdcGraphConfig:
        return IdcGraphConfig(
            backend=self.backend,
            resource_init=self.resource,
            critical_threshold=self.critical_threshold,
            cost_per_token=self.cost_per_token,
            max_steps=self.max_steps,
            gain_fn=self.gain_fn,
            use_stop_rule=self.use_stop_rule,
            prefer_ignorance_if_no_useful=self.prefer_ignorance_if_no_useful,
            useful_gain_floor=self.useful_gain_floor,
        )

    def run(self, task: str) -> IdcRunResult:
        cfg = self.config()
        state = initial_state(task, resource=self.resource, use_stop_rule=self.use_stop_rule)
        while not state.get("stopped"):
            state = deliberation_node(state, cfg)
            if int(state.get("step", 0)) >= cfg.max_steps:
                state["stopped"] = True
                state.update(_finalize(state, cfg))
                break
        if not state.get("answer"):
            state.update(_finalize(state, cfg))
        return state_to_result(state, cfg)

    def invoke(self, state: MutableMapping[str, Any]) -> IdcState:
        """API style LangGraph ``graph.invoke(state)``."""
        cfg = self.config()
        s: IdcState = initial_state(
            str(state.get("task", "")),
            resource=float(state.get("resource", self.resource)),
            use_stop_rule=bool(state.get("use_stop_rule", self.use_stop_rule)),
        )
        s.update({k: v for k, v in state.items() if k in s or k == "task"})
        while not s.get("stopped"):
            s = deliberation_node(s, cfg)
            if int(s.get("step", 0)) >= cfg.max_steps:
                s["stopped"] = True
                s.update(_finalize(s, cfg))
                break
        if not s.get("answer"):
            s.update(_finalize(s, cfg))
        return s


def compile_langgraph(
    backend: Backend,
    *,
    use_stop_rule: bool = True,
    resource: float = 100.0,
    critical_threshold: float = 15.0,
    cost_per_token: float = 0.8,
    max_steps: int = 8,
    gain_fn: Optional[GainFn] = None,
) -> Any:
    """Compile un vrai ``StateGraph`` LangGraph si le package est installé.

    Raises
    ------
    ImportError
        Message clair avec hint ``pip install idc-wrapper[langgraph]``.
    """
    StateGraph, END = require_langgraph()
    cfg = IdcGraphConfig(
        backend=backend,
        resource_init=resource,
        critical_threshold=critical_threshold,
        cost_per_token=cost_per_token,
        max_steps=max_steps,
        gain_fn=gain_fn or default_gain,
        use_stop_rule=use_stop_rule,
    )

    # État typé de façon souple (dict) pour rester compatible versions langgraph.
    graph = StateGraph(dict)

    def _node(state: dict) -> dict:
        return deliberation_node(state, cfg)

    def _route(state: dict) -> str:
        return should_continue(state)

    graph.add_node("deliberate", _node)
    graph.set_entry_point("deliberate")
    graph.add_conditional_edges(
        "deliberate",
        _route,
        {"continue": "deliberate", "end": END},
    )
    return graph.compile()


__all__ = [
    "LANGGRAPH_INSTALL_HINT",
    "IdcState",
    "IdcGraphConfig",
    "IdcGraphRunner",
    "initial_state",
    "deliberation_node",
    "should_continue",
    "state_to_result",
    "compile_langgraph",
    "require_langgraph",
]
