"""Minimal deterministic residence-gated controller simulation."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class ControllerParams:
    """Parameters for a generic residence-gated controller."""

    rhoa_input: float = 0.08
    rhoa_decay: float = 0.04
    window_low: float = 0.35
    window_high: float = 0.75
    window_slope: float = 0.05
    src_drive: float = 0.15
    src_decay: float = 0.08
    reserve_decay: float = 0.06
    reserve_recovery: float = 0.02
    myh9_gain: float = 0.20
    myh10_gain: float = 0.25


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))


def window_gate(rhoa: float, params: ControllerParams) -> float:
    """Return a smooth 0-1 gate for residence inside the RhoA window."""

    lower = sigmoid((rhoa - params.window_low) / params.window_slope)
    upper = sigmoid((params.window_high - rhoa) / params.window_slope)
    return lower * upper


def simulate_controller(
    *,
    duration: float = 20.0,
    dt: float = 0.5,
    params: ControllerParams | None = None,
    initial_rhoa: float = 0.45,
    initial_src: float = 0.20,
    initial_reserve: float = 0.80,
) -> list[dict[str, float]]:
    """Simulate a minimal controller with residence, Src, reserve, and routing."""

    if dt <= 0 or duration < 0:
        raise ValueError("duration must be non-negative and dt must be positive")
    params = params or ControllerParams()
    rhoa = initial_rhoa
    src = initial_src
    reserve = initial_reserve
    rows: list[dict[str, float]] = []
    steps = int(duration / dt) + 1
    for step in range(steps):
        time = step * dt
        gate = window_gate(rhoa, params)
        myh9 = params.myh9_gain * rhoa
        myh10 = params.myh10_gain * src * (1.0 - reserve)
        burden = src * (1.0 - reserve)
        rows.append(
            {
                "time": time,
                "rhoa": rhoa,
                "window_gate": gate,
                "src": src,
                "reserve": reserve,
                "myh9_route": myh9,
                "myh10_route": myh10,
                "burden": burden,
            }
        )
        rhoa += dt * (params.rhoa_input - params.rhoa_decay * rhoa)
        src += dt * (params.src_drive * (1.0 - gate) - params.src_decay * src)
        reserve += dt * (params.reserve_recovery * gate - params.reserve_decay * src * reserve)
        reserve = max(0.0, min(1.0, reserve))
    return rows

