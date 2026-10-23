# Règle Cursor — charger la skill IDC

Quand la tâche touche à la **finitude**, l’**arrêt optimal**, le **coût des
hallucinations**, un **journal d’engagements**, ou l’**IDC** :

1. Lis et suis `agents/skills/idc/SKILL.md` (skill **IDC Effondrement décisionnel**).
2. Respecte le contrat `schema/idc-protocol.json` : ressource `R`, journal
   append-only, règle d’arrêt, collapse.
3. Préfère avouer l’ignorance plutôt qu’inventer quand `R` est bas.
4. Ne fabrique pas de métriques empiriques ; cite `PERFORMANCE.md` (mock) ou
   régénère via `benchmarks/bench_mock.py`.

Installation rapide : copie `agents/skills/idc/` dans ton dossier skills Cursor,
ou ajoute aussi [`idc.mdc`](./idc.mdc) sous `.cursor/rules/`.
