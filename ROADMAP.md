# Roadmap

Priorités honnêtes. Rien ici n’est promis comme déjà livré.

## Fait (v0.2.0)

- [x] Licence MIT, AGENTS.md, skill, schéma JSON
- [x] Package Python `python/idc/` + CLI + exemples 01–04
- [x] PERFORMANCE.md (mock reproductible, sans claims inventés)
- [x] CI GitHub Actions + release GitHub v0.2.0
- [x] Adaptateur LangGraph-shaped (stdlib + optionnel `langgraph`)
- [x] Crate Rust scindée `lib` + binaire mince
- [x] Packs Cursor / Claude / OpenAI Agents (stubs / snippets)
- [x] Workflow publish PyPI (OIDC) — **configuration publisher côté PyPI à faire**

## v0.3 — Distribution & qualité

- [ ] **PyPI live** : `pip install idc-wrapper` via trusted publisher OIDC
  (voir [PUBLISHING.md](./PUBLISHING.md))
- [ ] **crates.io** : publier `idc-wrapper` (lib) avec docs.rs
- [ ] Persistance optionnelle du journal (fichier / SQLite)
- [ ] VOI un cran plus fine (calibrage du seuil, tests unitaires dédiés)
- [ ] Topics GitHub (`agents`, `llm`, `stop-rule`, …) — à activer dans Settings
- [ ] Discussions GitHub activées (Settings → Features)

## v0.4 — Mesures réelles & adapters

- [ ] **Bench LLM réel** (OpenAI-compatible / local) : protocole documenté,
      scripts séparés du mock, **aucune** conflation avec les chiffres mock
- [ ] Plus d’adapters : OpenAI Agents SDK (au-delà du stub), CrewAI / AutoGen
      (interfaces claires, deps optionnelles)
- [ ] Exemple multi-agents avec journal partagé append-only
- [ ] Comparaison baseline vs IDC sur tâches ouvertes (rapport + caveats)

## Hors scope volontaire

- Claims de « survie AGI », FLOPS magiques, win-rates inventés
- Couplage obligatoire à un vendor cloud
- Réécriture du journal (contre le protocole)

Contributions : [CONTRIBUTING.md](./CONTRIBUTING.md) · idées : [community/GOOD_FIRST_ISSUES.md](./community/GOOD_FIRST_ISSUES.md).
