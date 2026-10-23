# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format s’inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Versionnage Sémantique](https://semver.org/lang/fr/).

## [Unreleased]

### Ajouté
- `ROADMAP.md` (v0.3 PyPI/crates.io ; v0.4 bench LLM réel + adapters).
- `PUBLISHING.md` + `.github/workflows/publish-pypi.yml` (OIDC trusted publishing).
- Packs agents : `packs/cursor/`, `packs/claude/`, `packs/openai-agents/` (stub + interface).
- `community/GOOD_FIRST_ISSUES.md` (3 textes prêts à coller).
- `docs/demo.md` (flux ASCII + Mermaid de la boucle IDC).
- Crate Rust scindée : `src/lib.rs` (API publique `IdcAgent`, `AppendOnlyJournal`) + `src/main.rs` mince.

### Modifié
- README : badges (licence, release v0.2.0, CI, Python, Rust), liens livre Amazon FR + `CITATION.cff`, section Roadmap, packs, pas de claims perf inventés.
- `Cargo.toml` : description, license MIT, repository, readme, keywords, categories, `[lib]` / `[[bin]]`.
- `CONTRIBUTING.md` : activer Discussions + topics (actions manuelles Settings).
- `pyproject.toml` : métadonnées publish-ready (URLs projet).

## [0.2.0] — 2026-10-23

### Ajouté
- Pack communautaire : `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, templates d’issues / PR, CI GitHub Actions.
- Package Python `python/idc/` (journal, agent, mock backend) ; `python/idc_agent.py` reste le CLI.
- Exemples `examples/01_support_client`, `02_code_assistant`, `03_research_synth` (Sans/Avec IDC + scripts mock).
- Micro-benchmarks mock `benchmarks/bench_mock.py` + `benchmarks/results/latest.json`.
- `PERFORMANCE.md` généré depuis les mesures réelles du mock (pas de chiffres inventés).
- `CITATION.cff`, `pyproject.toml`.
- **Adaptateur LangGraph-shaped** `python/idc/langgraph_adapter.py` :
  - `IdcGraphRunner` / `deliberation_node` / `should_continue` (stdlib, sans dépendance).
  - `compile_langgraph()` pour un vrai `StateGraph` si `langgraph` est installé
    (`pip install idc-wrapper[langgraph]`) ; sinon `ImportError` explicite.
  - Exemple `examples/04_langgraph/` (mock, aucune clé API).
  - Tests `test_langgraph_adapter.py` (CI verte sans langgraph).

### Modifié
- README enrichi (badges, TOC, quickstart, liens perf / exemples / communauté / LangGraph).
- Version package / Cargo / schéma → 0.2.0.

## [0.1.0] — 2026-10

### Ajouté
- Implémentation Rust initiale (`src/main.rs`).
- Agent Python stdlib (`python/idc_agent.py`).
- `AGENTS.md`, skill `agents/skills/idc/SKILL.md`, schéma `schema/idc-protocol.json`.
- Licence MIT.

[Unreleased]: https://github.com/lanoixdesign/idc-wrapper/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/lanoixdesign/idc-wrapper/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/lanoixdesign/idc-wrapper/releases/tag/v0.1.0
