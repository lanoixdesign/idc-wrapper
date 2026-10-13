# IDC Wrapper

**Couche d’enveloppe IDC (Effondrement Décisionnel Irréversible) en Rust.**

Ce projet implémente une couche de contrôle autour d’un LLM (compatible OpenAI) qui impose :

- une **ressource finie** `R` qui décroît avec le calcul,
- un **journal append-only** (engagements irréversibles),
- une **règle d’arrêt optimal** (arrêt quand la valeur de l’information ne justifie plus le coût).

L’objectif est de forcer une forme de finitude computationnelle pour obtenir des décisions plus rapides, moins coûteuses et potentiellement moins sujettes aux hallucinations.

## Concept

L’IDC ne remplace pas le modèle. Il l’enveloppe :

1. On initialise une ressource `R` (ex. 100).
2. À chaque étape de délibération, on appelle le LLM, on consomme de la ressource et on évalue si continuer vaut encore le coup.
3. Quand `R` approche un seuil critique ou que le gain marginal est faible, on s’arrête et on engage la réponse (effondrement).
4. Toutes les étapes sont consignées dans un journal irréversible.

## Prérequis

- Rust (edition 2021)
- Une clé API compatible OpenAI (variable d’environnement `OPENAI_API_KEY`)

## Compilation

```bash
cargo build --release
```

Le binaire se trouve dans `target/release/idc-wrapper`.

## Utilisation

```bash
export OPENAI_API_KEY=sk-...
./target/release/idc-wrapper
```

Par défaut, le programme utilise `https://api.openai.com/v1/chat/completions` et le modèle `gpt-4o-mini`.  
Tu peux modifier l’URL, la clé et le modèle directement dans `main()` ou en adaptant le constructeur `IdcAgent::new`.

### Paramètres ajustables

| Paramètre          | Valeur par défaut | Rôle                                      |
|--------------------|-------------------|--------------------------------------------|
| `resource`         | 100.0             | Budget initial de délibération            |
| `seuil_critique`   | 15.0              | Seuil en dessous duquel on force l’arrêt |
| `cout_par_token`   | 0.8               | Coût approximatif par token               |
| Nombre max d’étapes | 8             | Garde-fou                                  |

## Structure du code

- `AppendOnlyJournal` : journal irréversible.
- `IdcAgent` : agent qui gère la ressource, les appels au modèle et la décision d’arrêt.
- `vaut_encore_la_peine` : heuristique simple de valeur de l’information (VOI).
- `run` : boucle principale d’effondrement décisionnel.

## Améliorations possibles

- Estimation de VOI plus fine (entropie, petit modèle secondaire, etc.).
- Persistance du journal sur disque.
- Interface en bibliothèque (`lib.rs`) pour intégration dans d’autres projets.
- Support de endpoints locaux (Ollama, vLLM, etc.).
- Calibrage dynamique du coût et du seuil.

## Licence

MIT (ou à définir).

## Auteur

Micaël Lanoix — dans la continuité des travaux sur l’ADN numérique des images (PNGIA / Pixel 4D) et l’Effondrement Décisionnel Irréversible.
