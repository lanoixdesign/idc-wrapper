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
   cargo check   # si tu touches au Rust
   ```
5. **Ne invente pas** de résultats empiriques (FLOPS, taux de survie, win-rates LLM). Documente les hypothèses comme telles ; les benches mock doivent rester reproductibles.
6. Docs utilisateur principalement en **français** ; un court encadré EN est bienvenu.
7. Licence des contributions : MIT (même licence que le dépôt).

## English (short)

1. Open an issue before large design changes (stop rule, JSON protocol, public API).
2. Fork → `feat/...` or `fix/...` branch → PR to `main`.
3. Follow the [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).
4. Run mock tests/benches (no API keys). `cargo check` if you touch Rust.
5. **Do not invent** empirical claims. Label theory as hypothesis; keep mock benches reproducible.
6. User-facing docs primarily French; short English blurbs welcome.
7. Contributions under MIT.
