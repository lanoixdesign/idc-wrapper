---
name: IDC Effondrement décisionnel
description: >-
  Utiliser quand on explique, applique ou prolonge le modèle IDC (Effondrement
  Décisionnel Irréversible) : finitude pour l’AGI, design d’agent, cas Sans/Avec
  IDC, ou hypothèse hallucinations.
---
# IDC — Effondrement Décisionnel Irréversible

Cadre réutilisable tiré du concept : une IA sans finitude peut réfléchir sans fin, gaspiller du calcul, hésiter, et inventer des réponses parce qu’inventer ne coûte pas plus cher que d’avouer l’ignorance. L’IDC impose la finitude pour forcer une décision utile.

## Quand l’appliquer
- Expliquer le concept IDC (vulgarisé ou formel).
- Concevoir ou auditer un agent ou un flux de décision.
- Rédiger un cas d’application au format **Sans IDC / Avec IDC / Bénéfice**.
- Argumenter pourquoi l’aveu d’ignorance doit coûter moins cher que l’hallucination.

## Les trois piliers
1. **Ressource qui diminue** — Un budget de délibération (temps, pureté, énergie) baisse à mesure que l’agent réfléchit. Trop délibérer = mort cognitive (état inexploitable).
2. **Mémoire append-only** — Les engagements pris sont gravés ; pas de retour arrière indolore. Une action projette irréversiblement sur une branche et détruit les autres.
3. **Règle d’arrêt** — Décider (s’effondrer) quand l’utilité marginale de réfléchir encore ne vaut plus la perte de ressource. Heuristique du « assez bon maintenant » plutôt que l’optimum global illusoire.

## Hypothèse clé (hallucinations)
Aujourd’hui, une réponse fausse ne coûte souvent pas plus cher qu’un « je ne sais pas ». Sous IDC, fabriquer une réalité alternative coûteuse épuise la ressource vitale. L’hallucination devient défavorable : face à l’incertitude, préférer l’effondrement rapide sur l’aveu d’ignorance.

## Comment procéder
1. **Nommer le problème d’infinité** : backtracking illimité, calcul non pénalisé, pas de hiérarchie vitale de l’info.
2. **Poser les trois piliers** adaptés au contexte (pas forcément la math Lindblad ; garder le formalisme seulement si demandé).
3. **Choisir le niveau** :
   - Vulgarisé : métaphores (horloge vitale, engagement irréversible, urgence d’exister), accessible sans bagage technique.
   - Formel : matrice densité, Lindblad modifié, fonction d’arrêt optimale, append-only, simulation type Dynamic Cliff Maze.
4. **Cas d’application** — Pour chaque scénario (support, code, recherche, décision, agent autonome, modération, tuteur, ou autre) écrire trois blocs courts :
   - **Sans IDC** — symptôme (boucle, hésitation, invention).
   - **Avec IDC** — budget + arrêt + engagement.
   - **Bénéfice** — moins de calcul, décision plus nette, moins d’affabulation.
5. **Limites à rappeler** — calibrage du seuil, valeur de l’info, irréversibilité, domaines inadaptés, pas de garantie d’alignement magique, modèle à valider expérimentalement.
6. **Clôturer** — la thèse centrale : l’AGI n’émerge pas de l’empilement infini de calcul, mais de l’acceptation de la finitude (« l’urgence d’exister »).

## Ton et garde-fous
- Clair, concret, illustré ; éviter le jargon sauf demande formelle.
- Ne pas présenter l’IDC comme une preuve empirique déjà validée : c’est un modèle / hypothèse avec protocole de test.
- Ne pas inventer de résultats de simulation ; proposer le protocole (ex. QuTiP, labyrinthe dynamique) si on parle d’expérience.
- Garder les détails auteur, ASIN ou chemins de fichiers hors du skill ; ils vivent dans le contexte de la conversation.
