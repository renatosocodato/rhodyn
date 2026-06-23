"""Stochastic timing utilities."""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import log
from typing import Callable


State = dict[str, float]
Propensity = Callable[[State], float]


@dataclass(frozen=True)
class Reaction:
    """One stochastic reaction channel."""

    name: str
    change: dict[str, float]
    propensity: Propensity


def first_passage_time(times: list[float], values: list[float], threshold: float, *, direction: str = "above") -> float | None:
    """Return the first time a trajectory crosses a threshold."""

    if len(times) != len(values):
        raise ValueError("times and values must have the same length")
    if direction not in {"above", "below"}:
        raise ValueError("direction must be 'above' or 'below'")
    for time, value in zip(times, values):
        if direction == "above" and value >= threshold:
            return time
        if direction == "below" and value <= threshold:
            return time
    return None


def gillespie(
    initial: State,
    reactions: list[Reaction],
    *,
    duration: float,
    seed: int | None = None,
) -> list[tuple[float, State]]:
    """Run a simple exact stochastic simulation algorithm."""

    rng = random.Random(seed)
    time = 0.0
    state = dict(initial)
    rows: list[tuple[float, State]] = [(time, dict(state))]
    while time < duration:
        props = [max(0.0, reaction.propensity(state)) for reaction in reactions]
        total = sum(props)
        if total <= 0:
            break
        time += -log(max(rng.random(), 1e-12)) / total
        draw = rng.random() * total
        cumulative = 0.0
        chosen = reactions[-1]
        for reaction, propensity in zip(reactions, props):
            cumulative += propensity
            if draw <= cumulative:
                chosen = reaction
                break
        for key, delta in chosen.change.items():
            state[key] = state.get(key, 0.0) + delta
        rows.append((time, dict(state)))
    return rows


def tau_leap(
    initial: State,
    reactions: list[Reaction],
    *,
    duration: float,
    tau: float,
    seed: int | None = None,
) -> list[tuple[float, State]]:
    """Run a lightweight tau-leap approximation.

    This uses a Knuth Poisson sampler to avoid external dependencies.
    """

    if tau <= 0:
        raise ValueError("tau must be positive")
    rng = random.Random(seed)
    time = 0.0
    state = dict(initial)
    rows: list[tuple[float, State]] = [(time, dict(state))]
    while time < duration:
        for reaction in reactions:
            lam = max(0.0, reaction.propensity(state) * tau)
            count = _poisson(lam, rng)
            for key, delta in reaction.change.items():
                state[key] = state.get(key, 0.0) + count * delta
        time += tau
        rows.append((time, dict(state)))
    return rows


def _poisson(lam: float, rng: random.Random) -> int:
    if lam <= 0:
        return 0
    limit = pow(2.718281828459045, -lam)
    k = 0
    p = 1.0
    while p > limit:
        k += 1
        p *= rng.random()
    return k - 1

