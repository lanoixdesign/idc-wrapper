# AGENTS.md — IDC for any agent runtime

This repository is designed so **any agent** (Cursor, Claude Code, Codex, OpenAI Agents, LangGraph, custom loops, etc.) can apply **Irreversible Decision Collapse (IDC)** without depending on a single vendor.

## Quick start for agents

1. Load `agents/skills/idc/SKILL.md` when the task involves AGI finitude, decision stopping, hallucination cost, or IDC case studies.
2. Prefer the **protocol** in `schema/idc-protocol.json` over hardcoding heuristics.
3. If you need an executable loop:
   - **Rust** (OpenAI-compatible HTTP): `cargo run --release` (see README)
   - **Python** (stdlib + urllib, OpenAI-compatible): `python python/idc_agent.py "your task"`
4. Always keep an **append-only journal** of commitments; never rewrite past entries.
5. Prefer **admit ignorance** when resource is low or confidence is weak — inventing is more expensive under IDC.

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

## Skill install (Cursor / Grok Bot style)

Copy `agents/skills/idc/` into your skills folder, or `@` / load the skill by name **IDC Effondrement décisionnel**.

## Interop

Agents may wrap any chat model that speaks OpenAI Chat Completions (`OPENAI_API_KEY`, optional `OPENAI_BASE_URL`, `OPENAI_MODEL`). Local servers (Ollama, vLLM) work if they expose that API.
