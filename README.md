# IDC Wrapper

🌐 **Language / Langue** : English · [Français](./README.fr.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Release](https://img.shields.io/github/v/release/lanoixdesign/idc-wrapper?display_name=tag&sort=semver)](https://github.com/lanoixdesign/idc-wrapper/releases/tag/v0.2.0)
[![CI](https://github.com/lanoixdesign/idc-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/lanoixdesign/idc-wrapper/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./python/)
[![Rust](https://img.shields.io/badge/rust-2021-orange.svg)](./Cargo.toml)

**IDC wrapper layer — Irreversible Decision Collapse (*Effondrement Décisionnel Irréversible*)**  
Open source, designed for **all agent runtimes** (Cursor, Claude Code, LangGraph, OpenAI Agents, custom loops…).

> Finite deliberation budget `R`, append-only journal, optimal stop rule.
> Hallucination should cost more than admitting ignorance. Mock benches are real
> numbers on a fake LLM; theory remains hypothesis — see [PERFORMANCE.md](./PERFORMANCE.md).

## Why IDC (vision, no invented claims)

An AI without **finitude** can deliberate endlessly, hesitate, and make things up: making
things up often costs no more than admitting "I don't know". IDC proposes
wrapping the model with:

1. a **finite resource** `R` that decreases with computation,
2. an **append-only journal** (irreversible commitments),
3. a **stop rule** (collapse when the marginal value of deliberating
   no longer justifies the cost).

It is a **model + test protocol**, not empirical proof already validated
on frontier LLMs. The numbers in this repository come from a reproducible
**mock** — see [PERFORMANCE.md](./PERFORMANCE.md).

## Book / concept

- Book (Amazon FR): [Effondrement Décisionnel Irréversible](https://www.amazon.fr/dp/B0HMX1CY6R)
- Machine-readable citation: [`CITATION.cff`](./CITATION.cff)

## Table of contents

- [For agents](#for-agents)
- [Python quickstart](#python-quickstart)
- [Rust quickstart](#rust-quickstart)
- [Examples](#examples)
- [LangGraph adapter](#langgraph-adapter)
- [Agent packs](#agent-packs)
- [Performance (mock)](#performance-mock)
- [Research & live benchmarks](#research--live-benchmarks)
- [Structure](#structure)
- [Parameters](#parameters)
- [Roadmap](#roadmap)
- [Community](#community)
- [License & author](#license--author)

## For agents

Read **[AGENTS.md](./AGENTS.md)** first.

| File | Role |
|---------|------|
| [`agents/skills/idc/SKILL.md`](./agents/skills/idc/SKILL.md) | Portable skill / recipe |
| [`schema/idc-protocol.json`](./schema/idc-protocol.json) | Machine-readable contract |
| [`python/idc/`](./python/idc/) | Reference package (journal, agent, mock) |
| [`python/idc/langgraph_adapter.py`](./python/idc/langgraph_adapter.py) | LangGraph-shaped adapter (optional) |
| [`python/idc_agent.py`](./python/idc_agent.py) | CLI (OpenAI-compatible or `--mock`) |
| [`src/lib.rs`](./src/lib.rs) | Rust library (`IdcAgent`, journal) |
| [`src/main.rs`](./src/main.rs) | Thin CLI binary |
| [`examples/`](./examples/) | Without IDC / With IDC cases |
| [`packs/`](./packs/) | Cursor / Claude / OpenAI Agents snippets |
| [`PERFORMANCE.md`](./PERFORMANCE.md) | Mock measurements + hypotheses vs demonstrated |

## Python quickstart

```bash
# Demo without an API key (recommended to get started)
PYTHONPATH=python python3 python/idc_agent.py --mock support_client \
  "Client : où est mon colis ?"

# Compare baseline (no VOI) vs IDC
PYTHONPATH=python python3 python/idc_agent.py --mock verbose --baseline "long"
PYTHONPATH=python python3 python/idc_agent.py --mock verbose "long"

# With an OpenAI-compatible API
export OPENAI_API_KEY=sk-...
# optional: OPENAI_BASE_URL=http://localhost:11434/v1  OPENAI_MODEL=llama3.2
PYTHONPATH=python python3 python/idc_agent.py "Explique l’IDC en 5 points"
```

Package installation (local editable; public PyPI planned — see [PUBLISHING.md](./PUBLISHING.md)):

```bash
pip install -e .
# or later: pip install idc-wrapper
```

Tests / bench (no key):

```bash
PYTHONPATH=python python3 -m unittest discover -s python/idc -v
PYTHONPATH=python python3 benchmarks/bench_mock.py
```

## Rust quickstart

```bash
cargo build --release
export OPENAI_API_KEY=sk-...
./target/release/idc-wrapper
```

The logic lives in the **lib crate** `idc_wrapper` (`src/lib.rs`); the binary
`src/main.rs` only calls it. Defaults: `https://api.openai.com/v1/chat/completions`,
model `gpt-4o-mini`.

> **Toolchain note**: `cargo check` / `cargo build` require a recent stable Rust
> (CI uses `dtolnay/rust-toolchain@stable`). If your local `rustc` is
> too old for the dependencies (`reqwest` / `tokio`), the lib+bin structure
> remains valid — update the toolchain or polish in CI.

## Examples

Concrete cases with a **Without IDC / With IDC / Benefit** narrative and mock scripts:

| # | Folder | Idea |
|---|---------|------|
| 01 | [`examples/01_support_client`](./examples/01_support_client/) | Delivery support |
| 02 | [`examples/02_code_assistant`](./examples/02_code_assistant/) | Bug fix + stop before a phantom API |
| 03 | [`examples/03_research_synth`](./examples/03_research_synth/) | Bounded synthesis, no invented citation |
| 04 | [`examples/04_langgraph`](./examples/04_langgraph/) | LangGraph-style node/state loop + IDC stop |
| 05 | [`examples/05_swarm_agents`](./examples/05_swarm_agents/) | Multi-agent swarm, `--idc` / `--no-idc` toggle |

See [`examples/README.md`](./examples/README.md). ASCII/Mermaid flow: [`docs/demo.md`](./docs/demo.md).

## LangGraph adapter

LangGraph-compatible **node / state** loop, **with no mandatory dependency**:

```bash
# mock demo (stdlib)
PYTHONPATH=python python3 examples/04_langgraph/run_mock.py

# optional: real StateGraph
pip install 'idc-wrapper[langgraph]'   # or: pip install langgraph
```

```python
from idc.langgraph_adapter import IdcGraphRunner, compile_langgraph
# IdcGraphRunner: always available
# compile_langgraph(...): clear ImportError if langgraph is missing
```

Details: [`examples/04_langgraph/README.md`](./examples/04_langgraph/README.md).

## Agent packs

Ready-to-paste snippets:

| Runtime | Pack |
|---------|------|
| Cursor | [`packs/cursor/RULE.md`](./packs/cursor/RULE.md) + [`packs/cursor/idc.mdc`](./packs/cursor/idc.mdc) |
| Claude Code | [`packs/claude/CLAUDE.md`](./packs/claude/CLAUDE.md) |
| OpenAI Agents SDK | [`packs/openai-agents/README.md`](./packs/openai-agents/README.md) (interface + stub) |

## Performance (mock)

Micro-benchmark **Baseline (fixed N) vs IDC (stop rule)** on mock responses.
Latest typical aggregate (regenerate locally to confirm):

| Aggregate | Baseline | IDC |
|---------|----------|-----|
| Mean steps | 8.0 | ~3.4 |
| Mean tokens≈ | ~44.8 | ~26.6 |
| Mean final R | ~64.2 | ~78.7 |

Details, caveats, and the distinction **book hypothesis vs demonstrated by the code**:
**[PERFORMANCE.md](./PERFORMANCE.md)**. No real-LLM performance claim here.

## Research & live benchmarks

To move from hypothesis to measurement, the repository contains a **pre-registered protocol**
and a **reproducible harness** on real models (Groq API):

- **[docs/PROTOCOL.md](./docs/PROTOCOL.md)** (French original; English translation:
  [docs/PROTOCOL.en.md](./docs/PROTOCOL.en.md)) — questions, falsifiable hypotheses H1–H7,
  6 axes (efficiency, stop calibration, multi-step robustness, swarm with shared `R`,
  traceability, honesty/abstention), conditions `sans_idc` (without IDC) / `r_seule` (R only) /
  `voi_seul` (VOI only) / `idc` + control `un_appel` (single call; amendment 1), blind judge, statistics (per-task bootstrap, McNemar),
  threats to validity, long-run plan.
- **[benchmarks/](./benchmarks/README.md)** — 81 versioned tasks
  (`tasks/idc_tasks_v1.jsonl`), runner with resumption and quota handling,
  judge, analysis → **[benchmarks/results/live/REPORT.md](./benchmarks/results/live/REPORT.md)**.

```bash
export GROQ_API_KEY=...
python3 benchmarks/run_bench.py --models allam-2-7b qwen/qwen3.8-27b openai/gpt-oss-20b \
  --conditions sans_idc idc un_appel r_seule voi_seul --repeats 10
python3 benchmarks/judge_bench.py && python3 benchmarks/analyze_bench.py
```

> **Status (24/10/2026): partial pilot run**, interrupted by Groq free-tier quotas
> (3 subject models, 1 repetition, conditions `sans_idc` / `idc` / `un_appel`; ablations
> `r_seule` / `voi_seul` not yet run; some of the runs not yet judged).
> The pilot signals (fewer tokens and loops with IDC, effect on
> hallucinations not significant at this stage) **do not allow concluding** a
> general gain: see the report and its intervals. The long-run pass resumes where it
> stopped (resumption by `run_id`).

## Structure

```
idc-wrapper/
├── AGENTS.md                 # contract for agent runtimes
├── PERFORMANCE.md            # honest mock measurements
├── ROADMAP.md                # v0.3 / v0.4
├── PUBLISHING.md             # PyPI trusted publisher
├── python/idc/               # package (journal, agent, mock, langgraph_adapter)
├── python/idc_agent.py       # CLI
├── src/lib.rs                # public Rust crate
├── src/main.rs               # thin binary
├── schema/idc-protocol.json
├── agents/skills/idc/SKILL.md
├── packs/                    # Cursor / Claude / OpenAI Agents
├── examples/                 # 4 cases + README (incl. LangGraph)
├── docs/demo.md              # IDC flow (ASCII / Mermaid)
├── benchmarks/               # bench_mock.py + results/
├── community/                # ready-to-paste good-first-issues
└── .github/                  # CI, publish-pypi, templates
```

## Parameters

| Parameter | Default | Role |
|-----------|--------|------|
| `resource` | 100.0 | Initial budget |
| `critical_threshold` | 15.0 | Forces the stop |
| `cost_per_token` | 0.8 | Approx. cost per token |
| `max_steps` | 8 | Safeguard |

Simple VOI heuristic: `estimated_gain > cost_per_token * 50 * risk`.

## Roadmap

v0.3 / v0.4 priorities (PyPI live, crates.io, real-LLM bench, more adapters):
**[ROADMAP.md](./ROADMAP.md)**.

## Community

- Contribute: [CONTRIBUTING.md](./CONTRIBUTING.md) (FR + EN) — also enable **Discussions** (Settings → Features)
- Conduct: [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- Security: [SECURITY.md](./SECURITY.md)
- Changelog: [CHANGELOG.md](./CHANGELOG.md)
- Good first issues: [community/GOOD_FIRST_ISSUES.md](./community/GOOD_FIRST_ISSUES.md)
- Issues / PRs: templates in `.github/`
- PyPI publishing: [PUBLISHING.md](./PUBLISHING.md)

Ideas welcome: finer VOI, on-disk journal persistence, crates.io publish,
real Agents SDK adapter, dynamic threshold calibration — **with reproducible
measurements**, no invented numbers. (LangGraph-shaped adapter: v0.2.0.)

## License & author

[MIT](./LICENSE) — Copyright (c) 2026 Micaël Lanoix

**Micaël Lanoix** — continuing work on the digital DNA of images
(PNGIA / Pixel 4D) and Irreversible Decision Collapse (*Effondrement Décisionnel Irréversible*).

Citation: see [`CITATION.cff`](./CITATION.cff). Book: [Amazon FR](https://www.amazon.fr/dp/B0HMX1CY6R).
