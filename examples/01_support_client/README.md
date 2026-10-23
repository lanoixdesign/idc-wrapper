# 01 — Support client (livraison)

## Sans IDC
L'agent reformule, invente un numéro de suivi, promet une date, recommence.
Coût tokens ↑, confiance client ↓, pas d'engagement net.

## Avec IDC
Budget `R` fini + journal append-only + arrêt quand le gain marginal < coût.
Diagnostic → cause → action engagée → **effondrement** (réponse utile ou aveu).

## Bénéfice
Moins d'étapes, ressource préservée, hallucination (suivi fantôme) jamais atteinte
dans le scénario mock car l'arrêt intervient avant.

## Exécuter

```bash
python examples/01_support_client/run_mock.py
```
