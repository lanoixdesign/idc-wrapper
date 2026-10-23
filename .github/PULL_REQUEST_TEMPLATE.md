## Résumé
<!-- Pourquoi ce PR ? -->

## Type
- [ ] fix
- [ ] feat
- [ ] docs
- [ ] chore / CI
- [ ] breaking (protocole / API)

## Checklist
- [ ] Tests mock OK (`unittest` + `bench_mock.py`) sans clé API
- [ ] Pas de secrets commités
- [ ] Pas de résultats empiriques inventés (FLOPS, survival, etc.)
- [ ] Docs FR à jour si comportement utilisateur changé
- [ ] `CHANGELOG.md` mis à jour si visible utilisateur

## Comment tester
```bash
PYTHONPATH=python python3 -m unittest discover -s python/idc -v
```
