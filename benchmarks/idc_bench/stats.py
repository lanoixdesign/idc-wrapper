"""Statistiques : bootstrap par tâche (cluster), McNemar exact, kappa de Cohen."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Callable, Iterable


def cluster_bootstrap(items: list[tuple[str, float]], n_boot: int = 2000, seed: int = 0,
                      alpha: float = 0.05) -> tuple[float | None, float | None, float | None]:
    """items = [(cluster_id, valeur)] ; renvoie (moyenne, borne basse, borne haute)."""
    if not items:
        return None, None, None
    groups: dict[str, list[float]] = defaultdict(list)
    for k, v in items:
        groups[k].append(v)
    keys = list(groups)
    mean = sum(v for _, v in items) / len(items)
    rng = random.Random(seed)
    stats = []
    for _ in range(n_boot):
        s, n = 0.0, 0
        for _ in keys:
            g = groups[keys[rng.randrange(len(keys))]]
            s += sum(g)
            n += len(g)
        stats.append(s / n)
    stats.sort()
    lo = stats[int((alpha / 2) * n_boot)]
    hi = stats[min(int((1 - alpha / 2) * n_boot), n_boot - 1)]
    return mean, lo, hi


def mcnemar_exact(pairs: Iterable[tuple[bool, bool]]) -> dict:
    """pairs = [(résultat_A, résultat_B)] ; test binomial bilatéral sur discordants."""
    b = c = n = 0
    for a, bb in pairs:
        n += 1
        if a and not bb:
            b += 1
        elif bb and not a:
            c += 1
    k, m = min(b, c), b + c
    if m == 0:
        p = 1.0
    else:
        p = min(1.0, 2 * sum(math.comb(m, i) for i in range(k + 1)) / (2 ** m))
    return {"n_pairs": n, "a_only": b, "b_only": c, "p": p}


def cohen_kappa(pairs: list[tuple[bool, bool]]) -> float | None:
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for a, b in pairs if a == b) / n
    pa = sum(1 for a, _ in pairs if a) / n
    pb = sum(1 for _, b in pairs if b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def fmt_ci(t: tuple, pct: bool = True, nd: int = 0) -> str:
    m, lo, hi = t
    if m is None:
        return "—"
    if pct:
        return f"{100*m:.{nd}f} % [{100*lo:.{nd}f}–{100*hi:.{nd}f}]"
    return f"{m:.{nd}f} [{lo:.{nd}f}–{hi:.{nd}f}]"
