# Publier sur PyPI

Ce dépôt est **prêt** pour une publication OIDC (trusted publishing).
**Aucun token n’est stocké ici** — tu dois configurer le publisher une fois.

## 1. Trusted publisher sur pypi.org

1. Crée (ou connecte) le projet **`idc-wrapper`** sur [pypi.org](https://pypi.org/).
2. Project → **Publishing** → **Add a new pending publisher** (Trusted Publishers).
3. Remplis :
   - **Owner** : `lanoixdesign`
   - **Repository** : `idc-wrapper`
   - **Workflow name** : `publish-pypi.yml`
   - **Environment name** : `pypi` (doit matcher le workflow)
4. Enregistre. La première publication GitHub Actions validera le lien.

Doc officielle : [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/).

## 2. Environment GitHub

Dans le dépôt → **Settings** → **Environments** → crée `pypi`
(protection rules optionnelles : reviewers, wait timer).

## 3. Déclenchement

Le workflow [`.github/workflows/publish-pypi.yml`](./.github/workflows/publish-pypi.yml)
se lance sur **`release: published`**.

1. Crée une GitHub Release (tag `v0.2.0` ou suivant) depuis l’UI ou le workflow `Release`.
2. Le job build (`python -m build`) puis upload via `pypa/gh-action-pypi-publish`
   avec `id-token: write` (pas de `PYPI_API_TOKEN` requis en mode OIDC).

### Fallback token (optionnel)

Si tu préfères un token classique : secret repo `PYPI_API_TOKEN`, et adapte
le step publish pour `password: ${{ secrets.PYPI_API_TOKEN }}`.
**Préférer OIDC** — moins de secrets à rotater.

## 4. Vérification locale (sans upload)

```bash
python -m pip install build twine
python -m build
twine check dist/*
# Ne pas twine upload sans publisher / token configuré.
```

## Checklist avant le premier upload

- [ ] `pyproject.toml` : name `idc-wrapper`, version alignée au tag
- [ ] Trusted publisher + environment `pypi` configurés
- [ ] CI verte sur `main`
- [ ] Release GitHub créée → workflow Publish to PyPI vert
