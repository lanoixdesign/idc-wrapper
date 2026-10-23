# AGENTS.md — IDC for any agent runtime

This repository is designed so **any agent** (Cursor, Claude Code, Codex, OpenAI Agents, LangGraph, custom loops, etc.) can apply **Irreversible Decision Collapse (IDC)** without depending on a single vendor.

## Quick start for agents

1. Load `agents/skills/idc/SKILL.md` when the task involves AGI finitude, decision stopping, hallucination cost, or IDC case studies.
2. Prefer the **protocol** in `schema/idc-protocol.json` over hardcoding heuristics.
3. If you need an executable loop:
   - **Python package** (stdlib): `python/idc/` — journal, agent, mock backend
   - **LangGraph-shaped adapter** (stdlib): `python/idc/langgraph_adapter.py` — `IdcGraphRunner` sans langgraph ; `compile_langgraph()` si `pip install idc-wrapper[langgraph]`
   - **Python CLI**: `PYTHONPATH=python python3 python/idc_agent.py --mock support_client "task"` (no API key) or with `OPENAI_API_KEY`
   - **Rust lib** (`idc_wrapper`): `src/lib.rs` — `IdcAgent`, `AppendOnlyJournal`; thin CLI `src/main.rs` via `cargo run --release`
   - **Packs**: `packs/cursor/`, `packs/claude/`, `packs/openai-agents/` (snippets / stub)
4. Always keep an **append-only journal** of commitments; never rewrite past entries.
5. Prefer **admit ignorance** when resource is low or confidence is weak — inventing is more expensive under IDC.
6. For demos of Sans/Avec IDC, run `examples/*/run_mock.py` (incl. `04_langgraph`, `05_swarm_agents` with `--idc`/`--no-idc`). For measured mock metrics, read `PERFORMANCE.md` (do not invent FLOPS/survival rates).

## Contract (minimal)

| Field | Meaning |
|-------|---------|
| `resource` | Finite deliberation budget; decreases each step |
| `critical_threshold` | Force stop below this |
| `journal` | Append-only list of commitments |
| `stop_when` | Marginal value of more thinking < marginal cost |
| `collapse` | Emit final answer (or "I don't know") and freeze |

## Do / Don't

- **Do** stop early when extra tokens won't change the decision.
- **Do** log every irreversible commitment.
- **Don't** treat backtracking as free.
- **Don't** invent facts when uncertainty is cheaper to admit.
- **Don't** claim IDC is empirically proven; treat it as a model + test protocol.
- **Don't** invent benchmark numbers; regenerate via `benchmarks/bench_mock.py`.

## Skill install (Cursor / Grok Bot style)

Copy `agents/skills/idc/` into your skills folder, or `@` / load the skill by name **IDC Effondrement décisionnel**.

## Interop

Agents may wrap any chat model that speaks OpenAI Chat Completions (`OPENAI_API_KEY`, optional `OPENAI_BASE_URL`, `OPENAI_MODEL`). Local servers (Ollama, vLLM) work if they expose that API. For offline demos, use `--mock` scenarios in `python/idc/mock_backend.py`.

## LangGraph

- Sans dépendance : `from idc.langgraph_adapter import IdcGraphRunner` puis `runner.run(task)` (boucle nœud/état).
- Avec LangGraph : `pip install idc-wrapper[langgraph]` puis `compile_langgraph(backend=...)`.
- Démo : `PYTHONPATH=python python3 examples/04_langgraph/run_mock.py`.
