"""
Helix Hamiltonian Core primitives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np

FORM_VALUES = {
    "FACT",
    "HYPOTHESIS",
    "ASSUMPTION",
    "QUESTION",
    "RECOMMEND",
    "EXECUTE",
}

VELOCITY_VALUES = {
    "PROCEED",
    "PAUSE",
    "ESCALATE",
    "STOP",
}


@dataclass
class Interaction:
    """RFC 0001 interaction tuple."""

    utterance: str
    form: str
    velocity: str
    authority: str
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.form not in FORM_VALUES:
            raise ValueError(f"Unsupported form: {self.form}")
        if self.velocity not in VELOCITY_VALUES:
            raise ValueError(f"Unsupported velocity: {self.velocity}")
        if self.context is None:
            self.context = {}


@dataclass
class NodeState:
    """Minimal local node state for bridge and federation checks."""

    node_id: str
    drift_score: float = 0.0
    authority_level: str = "ADVISORY"
    jones_polynomial: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnotHamiltonian:
    """
    Lightweight Hamiltonian facade used by the docs, bridge, and tests.
    """

    # Jones polynomial |V_K(e^{2πi/5})| for each knot type.
    # Values from ADR-105 extended knot testing.
    KNOT_INVARIANTS = {
        "0_1": 1.0,       # Unknot
        "3_1": 1.4142,    # Trefoil — |J| = √2
        "4_1": 2.6180,    # Figure-eight — |J| = φ + 1 (golden ratio + 1)
        "5_1": 1.9890,    # Cinquefoil T(2,5)
        "7_1": 2.2469,    # T(2,7) torus knot
        "9_1": 2.4940,    # T(2,9) torus knot
        "hopf": 1.9021,   # Hopf link (2-component)
    }

    def __init__(
        self,
        knot_type: str = "3_1",
        n_qubits: int = 1,
        omega_z: float = 1.0,
        omega_fold: float = 0.5,
        lambda_topo: float = 0.3,
    ) -> None:
        self.knot_type = knot_type
        self.n_qubits = n_qubits
        self.omega_z = omega_z
        self.omega_fold = omega_fold
        self.lambda_topo = lambda_topo
        self.gamma = 0.1
        self.J_K = self.KNOT_INVARIANTS.get(knot_type, 1.0)

    def get_h_free(self) -> np.ndarray:
        return (self.omega_z / 2.0) * np.array([[1.0, 0.0], [0.0, -1.0]])

    def get_h_fold(self) -> np.ndarray:
        sx = np.array([[0.0, 1.0], [1.0, 0.0]])
        sy = np.array([[0.0, -1j], [1j, 0.0]])
        return self.omega_fold * (sx + 1j * self.gamma * sy)

    def get_h_topo(self) -> np.ndarray:
        return self.lambda_topo * self.J_K * np.array([[1.0, 0.0], [0.0, -1.0]])

    def construct(self) -> np.ndarray:
        return self.get_h_free() + self.get_h_fold() + self.get_h_topo()

    def get_coherence_protection(self) -> float:
        return self.J_K

    def get_decoherence_suppression(self) -> float:
        return 1.0 / self.J_K if self.J_K else 0.0

    def get_effective_resistance(self, t: float, tau: float = 1.718) -> float:
        epsilon = 0.1
        wobble = epsilon * np.sin(2 * np.pi * t / tau)
        return 1.0 + float(wobble)


def verify_authority_ambiguity(substrate: Dict[str, Any]) -> Dict[str, str]:
    """
    GICD marker 1: only reject missing or malformed authority declarations.
    More specific jurisdictional checks belong in the authority layer.
    """

    authority = substrate.get("authority")
    if not isinstance(authority, str) or not authority.strip():
        return {"status": "FAIL", "details": "Authority ambiguity detected"}
    return {"status": "PASS"}


__all__ = [
    "FORM_VALUES",
    "Interaction",
    "KnotHamiltonian",
    "NodeState",
    "VELOCITY_VALUES",
    "verify_authority_ambiguity",
]
