# Good first issues — textes prêts à coller

Trois propositions concrètes. Tu peux les coller manuellement, ou elles ont
été (re)créées via l’API Issues si disponible. Labels suggérés :
`good first issue`, `help wanted`, `documentation` / `enhancement`.

---

## Issue 1 — Docs : glossaire FR/EN des termes IDC

**Title:** `[docs] Glossaire FR/EN des termes IDC (R, journal, collapse, VOI)`

**Labels:** `good first issue`, `documentation`

**Body:**

```markdown
### Contexte
Les nouveaux contributeurs croisent `R`, journal append-only, collapse, VOI,
seuil critique — sans page unique.

### Tâche
1. Ajouter `docs/glossary.md` (FR primaire + courte colonne EN).
2. Lier depuis le README (section Structure ou Communauté).
3. Pas de claims empiriques nouveaux.

### Critères d’acceptation
- [ ] Définitions pour : ressource R, seuil critique, journal append-only,
      règle d’arrêt / VOI, collapse, mock vs LLM réel
- [ ] Lien depuis README
- [ ] FR primaire

### Références
- `AGENTS.md`, `schema/idc-protocol.json`, `PERFORMANCE.md`
```

---

## Issue 2 — Exemple 05 : persistance journal JSONL

**Title:** `[enhancement] Exemple 05 — journal IDC persisté en JSONL`

**Labels:** `good first issue`, `enhancement`, `help wanted`

**Body:**

```markdown
### Contexte
Le journal est en mémoire. Un exemple reproductible (mock) qui append sur disque
aiderait les intégrations.

### Tâche
1. Créer `examples/05_journal_persist/` avec `README.md` (Sans/Avec) + `run_mock.py`.
2. Écrire chaque engagement en append-only dans un `.jsonl` (une ligne = un objet).
3. **Ne jamais** réécrire / truncate le fichier dans l’exemple.
4. Aucune clé API ; s’appuyer sur `python/idc/`.

### Critères d’acceptation
- [ ] Script mock vert en CI (ajouter au job `examples smoke` si prêt)
- [ ] README FR court
- [ ] Fichier JSONL produit dans un dossier tmp ou `examples/05_…/out/` gitignored

### Hors scope
Persistance SQLite production, sync cloud.
```

---

## Issue 3 — Tests unitaires Rust pour AppendOnlyJournal

**Title:** `[rust] Tests unitaires pour AppendOnlyJournal (lib)`

**Labels:** `good first issue`, `enhancement`

**Body:**

```markdown
### Contexte
`src/lib.rs` expose `AppendOnlyJournal` et `IdcAgent`. Pas encore de tests Rust
dans la CI au-delà de `cargo check`.

### Tâche
1. Ajouter des tests `#[cfg(test)]` dans `src/lib.rs` (ou `tests/journal.rs`) pour :
   - `append` / `as_context` / `len` / `is_empty`
   - vérifier qu’on ne fournit **pas** d’API de rewrite (pas de `clear` public, etc.)
2. Étendre `.github/workflows/ci.yml` : `cargo test` (en plus de `cargo check`).

### Critères d’acceptation
- [ ] `cargo test` vert sur toolchain stable CI
- [ ] Pas d’appel réseau dans les tests
- [ ] Docstring courte si besoin

### Note
Les deps HTTP peuvent exiger un rustc récent ; la CI utilise
`dtolnay/rust-toolchain@stable`.
```
