# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format s’inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Versionnage Sémantique](https://semver.org/lang/fr/).

## [0.2.0] — 2026-10-23

### Ajouté
- Pack communautaire : `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, templates d’issues / PR, CI GitHub Actions.
- Package Python `python/idc/` (journal, agent, mock backend) ; `python/idc_agent.py` reste le CLI.
- Exemples `examples/01_support_client`, `02_code_assistant`, `03_research_synth` (Sans/Avec IDC + scripts mock).
- Micro-benchmarks mock `benchmarks/bench_mock.py` + `benchmarks/results/latest.json`.
- `PERFORMANCE.md` généré depuis les mesures réelles du mock (pas de chiffres inventés).
- `CITATION.cff`, `pyproject.toml`.

### Modifié
- README enrichi (badges, TOC, quickstart, liens perf / exemples / communauté).
- Version package / Cargo → 0.2.0.

## [0.1.0] — 2026-10

### Ajouté
- Implémentation Rust initiale (`src/main.rs`).
- Agent Python stdlib (`python/idc_agent.py`).
- `AGENTS.md`, skill `agents/skills/idc/SKILL.md`, schéma `schema/idc-protocol.json`.
- Licence MIT.

[0.2.0]: https://github.com/lanoixdesign/idc-wrapper/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/lanoixdesign/idc-wrapper/releases/tag/v0.1.0
