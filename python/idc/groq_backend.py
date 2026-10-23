"""Backend Groq (API OpenAI-compatible) — stdlib uniquement.

Endpoint : https://api.groq.com/openai/v1/chat/completions
Clé : variable d'environnement ``GROQ_API_KEY`` uniquement (jamais hardcodée).

Heuristique de gain VOI (honnête, pédagogique — pas une mesure empirique) :
combine (1) un gain de base décroissant par round et (2) un score de
nouveauté lexical vs le journal déjà vu. Documentée pour que l'utilisateur
puisse la lire / la remplacer ; elle ne prétend pas prédire la valeur réelle
d'un token LLM en production.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
# Défaut public documenté (oct. 2026) : llama-3.3-70b-versatile est
# enterprise-only / déprécié sur free+developer ; gpt-oss-20b est production.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"

_WORD_RE = re.compile(r"[a-zA-Zàâäéèêëïîôùûüç0-9_]{2,}", re.UNICODE)


def _tokens(text: str) -> set[str]:
    return {m.group(0).lower() for m in _WORD_RE.finditer(text or "")}


@dataclass
class GroqBackend:
    """Client chat Groq via urllib (aucune dépendance hors stdlib).

    Compatible avec le protocole ``Backend`` (``generate``) et expose
    ``gain_for_step`` pour les runners essaim / agent qui en ont besoin.
    """

    api_key: str
    model: str = DEFAULT_GROQ_MODEL
    api_url: str = GROQ_CHAT_URL
    temperature: float = 0.4
    call_count: int = 0
    last_usage: dict | None = None
    prompt_tokens_total: int = 0
    completion_tokens_total: int = 0
    # Mots déjà vus dans les réponses précédentes (nouveauté).
    _seen_words: set[str] = field(default_factory=set)

    @classmethod
    def from_env(
        cls,
        model: str | None = None,
        *,
        temperature: float = 0.4,
    ) -> "GroqBackend":
        key = os.environ.get("GROQ_API_KEY", "").strip()
        if not key:
            raise SystemExit(
                "GROQ_API_KEY manquante. Exportez la clé Groq "
                "(https://console.groq.com/keys) puis relancez."
            )
        return cls(
            api_key=key,
            model=model or os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL),
            temperature=temperature,
        )

    def __call__(self, prompt: str, max_tokens: int = 120) -> str:
        return self.generate(prompt, max_tokens)

    def generate(self, prompt: str, max_tokens: int = 120) -> str:
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Groq HTTP {e.code}: {detail}") from e

        usage = data.get("usage") or {}
        self.last_usage = usage if isinstance(usage, dict) else None
        if self.last_usage:
            self.prompt_tokens_total += int(self.last_usage.get("prompt_tokens") or 0)
            self.completion_tokens_total += int(
                self.last_usage.get("completion_tokens") or 0
            )

        self.call_count += 1
        choices = data.get("choices") or []
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content") or ""

    def gain_for_step(self, step: int, chunk: str) -> float:
        """Heuristique VOI documentée (pas un claim empirique).

        Formule :
          base(step)   = max(8, 58 - 6 * (step - 1))  # décroissance par tour
          novelty      = |mots_nouveaux| / max(|mots_chunk|, 1)  ∈ [0, 1]
          length_factor = min(1, |mots| / 12)         # pénalise les bouts trop courts
          gain = base * (0.35 + 0.65 * novelty) * (0.35 + 0.65 * length_factor)

        Alignement pédagogique avec le mock : coût marginal ≈ cost_per_token*50
        (≈ 40 si cost_per_token=0.8). Un premier message riche en faits nouveaux
        reste au-dessus du seuil ; une reformulation ou un micro-chunk tombe
        en dessous. Ce n'est **pas** une mesure empirique de valeur LLM.
        """
        words = _tokens(chunk)
        if not words:
            # Pas de contenu → gain bas (favorise arrêt / ignorance)
            base = max(8.0, 58.0 - 6.0 * (step - 1))
            return min(base * 0.2, 12.0)

        new_words = words - self._seen_words
        novelty = len(new_words) / max(len(words), 1)
        self._seen_words |= words

        base = max(8.0, 58.0 - 6.0 * (step - 1))
        length_factor = min(1.0, len(words) / 12.0)
        gain = base * (0.35 + 0.65 * novelty) * (0.35 + 0.65 * length_factor)
        return round(gain, 2)

    def usage_summary(self) -> dict[str, int]:
        return {
            "calls": self.call_count,
            "prompt_tokens": self.prompt_tokens_total,
            "completion_tokens": self.completion_tokens_total,
            "total_tokens": self.prompt_tokens_total + self.completion_tokens_total,
        }
