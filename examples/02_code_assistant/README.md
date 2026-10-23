# 02 — Assistant code

## Sans IDC
L'agent enchaîne refactors, APIs inventées, suggestions hors scope.
Boucle jusqu'à épuisement du budget conversationnel.

## Avec IDC
Localiser → corriger → test → **stop** dès que le gain marginal s'effondre.
Les inventions d'API n'apparaissent pas dans le journal IDC du mock.

## Bénéfice
Patch minimal, journal court, moins de tokens gaspillés.

## Exécuter

```bash
python examples/02_code_assistant/run_mock.py
```
