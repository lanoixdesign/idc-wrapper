# Snippet CLAUDE.md — IDC

À coller / merger dans ton `CLAUDE.md` de projet (Claude Code).

```markdown
## IDC (Effondrement Décisionnel Irréversible)

Quand tu délibères longuement ou risques d’halluciner :

1. Charge la skill `agents/skills/idc/SKILL.md` et le schéma
   `schema/idc-protocol.json`.
2. Maintiens un journal append-only d’engagements.
3. Décrémente une ressource `R` à chaque étape de réflexion.
4. Arrête-toi (collapse) dès que le gain estimé ≤ coût marginal, ou si
   `R ≤ critical_threshold`.
5. Préfère « je ne sais pas » à une invention.
6. Ne cite pas de perf LLM réelles hors mesures documentées ; le mock est
   dans `PERFORMANCE.md`.

Quickstart mock :
`PYTHONPATH=python python3 python/idc_agent.py --mock support_client "…"`
```
