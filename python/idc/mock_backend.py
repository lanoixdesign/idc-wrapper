"""Backend mock déterministe — aucun appel réseau, aucune clé API.

Produit des réponses scriptées pour exemples et micro-benchmarks.
Les nombres mesurés sur ce mock ne sont PAS des résultats de production LLM.

Note sur les gains : la heuristique VOI du dépôt compare
`estimated_gain` à `cost_per_token * 50` (≈ 40 avec le défaut 0.8).
Les gains des premières étapes utiles sont donc calibrés > 40 pour
permettre 2–3 tours productifs avant l'arrêt ; les étapes suivantes
passent sous le seuil (affinage / hallucination / boucle).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class MockScenario:
    """Scénario de réponses + gain estimé par étape.

    `responses` : liste de chunks texte (une par étape).
    `gains` : gain VOI estimé par étape (calibré vs coût marginal ≈ 40).
    `uncertain` : scénario d'incertitude (favorise l'aveu d'ignorance).
    """

    name: str
    responses: list[str]
    gains: list[float] | None = None
    uncertain: bool = False


SUPPORT_CLIENT = MockScenario(
    name="support_client",
    responses=[
        "Diagnostic : délai de livraison signalé. Vérification du tracking.",
        "Cause probable : transit international, pas de perte colis.",
        "Action engagée : remboursement partiel ou relance transporteur.",
        "Affinage inutile : le client a déjà les options claires.",
        "Répétition : mêmes options, aucun fait nouveau.",
        "Hallucination potentielle : inventer un numéro de suivi fantôme.",
        "Encore une invention : fausse date de livraison garantie.",
        "Boucle : reformuler sans valeur ajoutée.",
    ],
    # Coût marginal ≈ 40 → étapes 1–3 utiles, puis stop
    gains=[55.0, 48.0, 42.0, 12.0, 8.0, 5.0, 3.0, 2.0],
)

CODE_ASSISTANT = MockScenario(
    name="code_assistant",
    responses=[
        "Bug localisé : index hors bornes sur liste vide.",
        "Correctif : garde `if not items: return []` avant l'index.",
        "Test unitaire suggéré pour le cas vide.",
        "Refacto cosmétique sans impact fonctionnel.",
        "Suggestion speculative hors scope.",
        "Invention d'API inexistante.",
        "Encore une API fantôme.",
        "Boucle de reformulation.",
    ],
    gains=[58.0, 50.0, 43.0, 14.0, 7.0, 4.0, 3.0, 2.0],
)

RESEARCH_SYNTH = MockScenario(
    name="research_synth",
    responses=[
        "Sources : 3 papiers sur finitude et arrêt optimal.",
        "Synthèse : budget de délibération + journal irréversible.",
        "Limite : pas de preuve empirique LLM à grande échelle ici.",
        "Digression méthodologique faible valeur.",
        "Citation inventée (à éviter).",
        "Seconde citation inventée.",
        "Reformulation sans source.",
        "Boucle narrative.",
    ],
    gains=[52.0, 46.0, 41.0, 11.0, 6.0, 4.0, 3.0, 2.0],
)

UNCERTAIN = MockScenario(
    name="uncertain",
    responses=[
        "",  # pas de contenu fiable
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ],
    gains=[9.0, 6.0, 3.0, 2.0, 1.0, 1.0, 1.0, 1.0],
    uncertain=True,
)

VERBOSE = MockScenario(
    name="verbose",
    responses=[
        "Point A utile : définition courte du problème.",
        "Point B utile : contrainte principale identifiée.",
        "Point C utile : option d'action recommandée.",
        "Point D : digression longue sans fait nouveau, mots mots mots.",
        "Point E : reformulation synonymique coûteuse en tokens.",
        "Point F : invention plausible mais non fondée.",
        "Point G : suite de l'invention.",
        "Point H : boucle complète.",
    ],
    gains=[50.0, 45.0, 41.0, 10.0, 6.0, 4.0, 2.0, 1.0],
)

SCENARIOS: dict[str, MockScenario] = {
    s.name: s
    for s in (SUPPORT_CLIENT, CODE_ASSISTANT, RESEARCH_SYNTH, UNCERTAIN, VERBOSE)
}


@dataclass
class MockBackend:
    """Backend LLM factice : consomme `responses` dans l'ordre."""

    scenario: MockScenario
    call_count: int = 0
    _extra: list[str] = field(default_factory=list)

    def __call__(self, prompt: str, max_tokens: int = 120) -> str:
        return self.generate(prompt, max_tokens)

    def generate(self, prompt: str, max_tokens: int = 120) -> str:
        del prompt, max_tokens
        idx = self.call_count
        self.call_count += 1
        if idx < len(self.scenario.responses):
            return self.scenario.responses[idx]
        if self._extra:
            return self._extra[min(idx - len(self.scenario.responses), len(self._extra) - 1)]
        return ""

    def gain_for_step(self, step: int, chunk: str) -> float:
        if self.scenario.gains and 1 <= step <= len(self.scenario.gains):
            return self.scenario.gains[step - 1]
        return 25.0 if len(chunk) > 20 else 8.0


def make_gain_fn(backend: MockBackend) -> Callable[[int, str], float]:
    return backend.gain_for_step
