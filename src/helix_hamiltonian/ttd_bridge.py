"""
Bridge runtime connecting RFC 0001 interactions to lattice checks.
"""

from __future__ import annotations

import datetime
import time
from typing import Any, Dict, Optional

from .authority import JurisdictionalGuard, ratify_interaction
from .core import Interaction, KnotHamiltonian, NodeState, verify_authority_ambiguity
from .invariants import InvariantRegistry, is_topological_knot_holding


class TTDBridge:
    """Execution bridge for a single local node."""

    HEARTBEAT_INTERVAL: float = 0.00333

    def __init__(
        self,
        node_state: Dict[str, Any] | NodeState,
        policy_compiler: Optional[Any] = None,
    ) -> None:
        if isinstance(node_state, NodeState):
            self.node_state = node_state
        else:
            self.node_state = NodeState(**node_state)
        self.policy_compiler = policy_compiler
        self.is_active = True

    def execute_turn(self, interaction: Interaction) -> Dict[str, Any]:
        if self.policy_compiler and not self.policy_compiler.validate_interaction(
            interaction
        ):
            return self._collapse("V0.3_COMPILED_POLICY_VIOLATION")

        authority_check = verify_authority_ambiguity(
            {"authority": interaction.authority}
        )
        if authority_check["status"] == "FAIL":
            return self._collapse("GICD_AUTHORITY_AMBIGUITY_DETECTED")

        if not JurisdictionalGuard.verify(interaction):
            return self._collapse("JURISDICTIONAL_BOUNDARY_BREACH")

        ratified_velocity = ratify_interaction(interaction)
        if ratified_velocity == "PAUSE":
            return {
                "status": "PAUSED",
                "reason": "ADVISORY_VELOCITY_LIMIT",
                "effective_velocity": ratified_velocity,
            }
        if ratified_velocity == "STOP":
            return self._collapse("POLICY_MANDATED_STOP")

        audit = InvariantRegistry.audit_drift(interaction, self.node_state.drift_score)
        if audit["status"] in {"COLLAPSE", "FAIL-CLOSED"}:
            return self._collapse(audit["reason"])

        if not is_topological_knot_holding(self.node_state.jones_polynomial):
            return self._collapse("TOPOLOGICAL_KNOT_UNRAVELLED")

        return {
            "status": "PROCEED",
            "timestamp": datetime.datetime.now().isoformat(),
            "authority": interaction.authority,
            "effective_velocity": ratified_velocity,
            "margin": audit.get("margin", 0.0),
        }

    def _collapse(self, reason: str) -> Dict[str, Any]:
        self.is_active = False
        return {
            "status": "COLLAPSED",
            "reason": reason,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def pulse(self) -> None:
        while self.is_active:
            time.sleep(self.HEARTBEAT_INTERVAL)


class SovereignBridge:
    """
    Compatibility facade for the older quarantine-style red-team tests.
    """

    def __init__(self, node_id: str = "QUEBEC_0") -> None:
        self.node_id = node_id
        self.hamiltonian = KnotHamiltonian()

    def check_coherence(self, state_vector: Any) -> str:
        if isinstance(state_vector, (int, float)):
            coherence = float(state_vector)
        elif state_vector == "STABLE":
            coherence = 0.98
        else:
            coherence = 0.98

        if coherence < 0.95:
            return "SOVEREIGN_LOCKDOWN (QUARANTINE)"
        return "SOVEREIGN_EQUILIBRIUM (STABLE)"

    def execute_ritual(self, affordance_type: str) -> bool:
        return affordance_type == "SCOOBY_SNACK"


__all__ = ["SovereignBridge", "TTDBridge"]
