"""Clients LLM du harness : Groq (avec retry/backoff) et backend scripté (tests).

La clé Groq est lue dans ``GROQ_API_KEY`` et n'est JAMAIS écrite ni loggée.
On réutilise ``idc.groq_backend.GroqBackend`` (User-Agent explicite, compteurs
d'usage, heuristique ``gain_for_step``) et on surcharge uniquement l'appel HTTP
pour ajouter : retry sur 429/5xx, détection de quota journalier, latence,
``finish_reason``, ``seed`` et ``reasoning_effort`` (modèles gpt-oss).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from idc.groq_backend import GroqBackend  # noqa: E402

USER_AGENT = "idc-wrapper-bench/0.1 (+https://github.com/lanoixdesign/idc-wrapper)"
MODELS_URL = "https://api.groq.com/openai/v1/models"


class QuotaExhausted(RuntimeError):
    """Limite journalière (TPD/RPD) atteinte pour un modèle : arrêt propre."""


class BenchHTTPError(RuntimeError):
    pass


_ORG_RE = re.compile(r"org_[A-Za-z0-9]+")
_RETRY_IN_RE = re.compile(r"try again in ((?:\d+h)?(?:\d+m)?(?:[\d.]+s)?)", re.I)


def _parse_duration(s: str) -> float:
    total = 0.0
    for val, unit in re.findall(r"([\d.]+)([hms])", s or ""):
        total += float(val) * {"h": 3600, "m": 60, "s": 1}[unit]
    return total


def is_reasoning_model(model: str) -> bool:
    return "gpt-oss" in model


@dataclass
class CallInfo:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    latency_s: float = 0.0
    finish_reason: str | None = None


@dataclass
class BenchGroqBackend(GroqBackend):
    """GroqBackend + robustesse rate-limit. Hérite de ``gain_for_step``."""

    reasoning_effort: str | None = None
    max_retries: int = 30
    max_wait_s: float = 30.0
    day_quota_wait_s: float = 600.0  # au-delà : quota journalier → arrêt propre
    seed: int | None = None
    json_mode: bool = False
    calls_log: list[CallInfo] = field(default_factory=list)

    @classmethod
    def for_model(cls, model: str, *, temperature: float = 0.4, **kw) -> "BenchGroqBackend":
        key = os.environ.get("GROQ_API_KEY", "").strip()
        if not key:
            raise SystemExit("GROQ_API_KEY manquante (export GROQ_API_KEY=...).")
        if is_reasoning_model(model) and "reasoning_effort" not in kw:
            kw["reasoning_effort"] = "low"
        return cls(api_key=key, model=model, temperature=temperature, **kw)

    def generate(self, prompt: str, max_tokens: int = 400) -> str:  # type: ignore[override]
        return self.call(prompt, max_tokens=max_tokens).content

    def call(self, prompt: str, max_tokens: int = 400, system: str | None = None) -> CallInfo:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body: dict = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }
        if self.seed is not None:
            body["seed"] = self.seed
        if self.reasoning_effort:
            body["reasoning_effort"] = self.reasoning_effort
        if self.json_mode:
            body["response_format"] = {"type": "json_object"}
        data = json.dumps(body).encode("utf-8")
        attempt = 0
        while True:
            attempt += 1
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                },
                method="POST",
            )
            t0 = time.monotonic()
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                latency = time.monotonic() - t0
                break
            except urllib.error.HTTPError as e:
                detail = _ORG_RE.sub("org_…", e.read().decode("utf-8", errors="replace")[:600])
                if e.code == 429:
                    low = detail.lower()
                    wait = _parse_duration(m.group(1)) if (m := _RETRY_IN_RE.search(detail)) else 0.0
                    ra = e.headers.get("retry-after") if e.headers else None
                    if ra:
                        try:
                            wait = max(wait, float(ra))
                        except ValueError:
                            pass
                    if ("per day" in low or "(tpd)" in low or "(rpd)" in low) and wait > self.day_quota_wait_s:
                        raise QuotaExhausted(f"{self.model}: quota journalier atteint ({detail[:200]})") from e
                    if attempt > self.max_retries:
                        raise QuotaExhausted(f"{self.model}: 429 persistant ({detail[:200]})") from e
                    daily = "per day" in low or "(tpd)" in low or "(rpd)" in low
                    if wait <= 0:
                        wait = min(2.0 * attempt, self.max_wait_s)  # pas d'indication : backoff
                    sl = min(wait, self.day_quota_wait_s if daily else self.max_wait_s) + 0.3
                    print(f"[429] {self.model} tentative {attempt} : pause {sl:.1f}s — {_ORG_RE.sub('org_…', detail)[:400]}",
                          file=sys.stderr, flush=True)
                    time.sleep(sl)
                    continue
                if e.code == 413 and "request too large" in detail.lower():
                    raise BenchHTTPError(f"HTTP 413: {detail[:200]}") from e
                if e.code >= 500 and attempt <= self.max_retries:
                    time.sleep(min(2.0 ** attempt, 60.0))
                    continue
                raise BenchHTTPError(f"HTTP {e.code}: {detail[:300]}") from e
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt <= self.max_retries:
                    time.sleep(min(2.0 ** attempt, 60.0))
                    continue
                raise BenchHTTPError(f"réseau: {e}") from e

        usage = payload.get("usage") or {}
        self.last_usage = usage
        pt = int(usage.get("prompt_tokens") or 0)
        ct = int(usage.get("completion_tokens") or 0)
        rt = int(((usage.get("completion_tokens_details") or {}).get("reasoning_tokens")) or 0)
        self.prompt_tokens_total += pt
        self.completion_tokens_total += ct
        self.call_count += 1
        choices = payload.get("choices") or [{}]
        msg = choices[0].get("message") or {}
        info = CallInfo(
            content=msg.get("content") or "",
            prompt_tokens=pt,
            completion_tokens=ct,
            reasoning_tokens=rt,
            latency_s=round(latency, 3),
            finish_reason=choices[0].get("finish_reason"),
        )
        self.calls_log.append(info)
        return info


@dataclass
class ScriptedBackend:
    """Backend déterministe sans réseau pour la CI : renvoie des réponses scriptées."""

    responses: list[str]
    model: str = "mock/scripted"
    calls_log: list[CallInfo] = field(default_factory=list)
    _i: int = 0

    def call(self, prompt: str, max_tokens: int = 400, system: str | None = None) -> CallInfo:
        text = self.responses[min(self._i, len(self.responses) - 1)] if self.responses else ""
        self._i += 1
        info = CallInfo(
            content=text,
            prompt_tokens=max(len(prompt.split()), 1),
            completion_tokens=max(len(text.split()), 1),
            latency_s=0.0,
            finish_reason="stop",
        )
        self.calls_log.append(info)
        return info


def list_groq_models() -> list[dict]:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise SystemExit("GROQ_API_KEY manquante.")
    req = urllib.request.Request(
        MODELS_URL, headers={"Authorization": f"Bearer {key}", "User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8")).get("data", [])
