# Contribuer / Contributing

Merci de ton intérêt pour **IDC Wrapper** (Effondrement Décisionnel Irréversible).

## Français (court)

1. Ouvre une *issue* avant un gros changement (design de la règle d’arrêt, protocole JSON, API publique).
2. Fork → branche `feat/...` ou `fix/...` → PR vers `main`.
3. Respecte le [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).
4. Tests sans clé API :
   ```bash
   PYTHONPATH=python python3 -m unittest discover -s python/idc -v
   PYTHONPATH=python python3 benchmarks/bench_mock.py
   cargo check   # si tu touches au Rust (toolchain stable récent recommandé)
   ```
5. **Ne invente pas** de résultats empiriques (FLOPS, taux de survie, win-rates LLM). Documente les hypothèses comme telles ; les benches mock doivent rester reproductibles.
6. Docs utilisateur principalement en **français** ; un court encadré EN est bienvenu.
7. Licence des contributions : MIT (même licence que le dépôt).

### Discussions GitHub

Les **Discussions** ne sont pas activables via l’API de ce bot. Pour les activer :

1. Repo → **Settings** → **General** → **Features**
2. Coche **Discussions**
3. (Optionnel) categories : Idées, Q&A, Show & tell

Ideas / questions longues → Discussions ; bugs & patches concrets → Issues.
Textes « good first issue » : [community/GOOD_FIRST_ISSUES.md](./community/GOOD_FIRST_ISSUES.md).

### Topics du dépôt

À ajouter manuellement (Settings → General → Topics), suggestions :
`agents`, `llm`, `python`, `rust`, `langgraph`, `stop-rule`, `finitude`, `mit-license`.

## English (short)

1. Open an issue before large design changes (stop rule, JSON protocol, public API).
2. Fork → `feat/...` or `fix/...` branch → PR to `main`.
3. Follow the [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).
4. Run mock tests/benches (no API keys). `cargo check` if you touch Rust (recent stable toolchain).
5. **Do not invent** empirical claims. Label theory as hypothesis; keep mock benches reproducible.
6. User-facing docs primarily French; short English blurbs welcome.
7. Contributions under MIT.

### GitHub Discussions

We cannot toggle Discussions via API. Enable under **Settings → Features → Discussions**.

### Repository topics

Set manually in Settings (no topics API used here). Suggested: `agents`, `llm`, `python`, `rust`, `langgraph`, `stop-rule`, `finitude`, `mit-license`.
