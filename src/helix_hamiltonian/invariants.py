"""
Helix Hamiltonian Invariants - Threshold Registry
Anchors the 0.17 drift constant and enforces topological integrity.
"""

from typing import Dict, Any, Final
from .core import Interaction

# --- THE UNIVERSAL CONSTANTS (RATIFIED MARCH 2026) ---
DRIFT_THRESHOLD_MAX: Final[float] = 0.17  # The '1,825-Day Hole' constant
SAFETY_MARGIN_RESERVE: Final[float] = 0.03  # The '0.20 Original Wobble' buffer

# Jurisdictional Drift Modifiers (Section 6.3)
# These adjust the sensitivity of the invariant check based on role stakes.
JURISDICTIONAL_SENSITIVITY: Dict[str, float] = {
    "CUSTODIAN_CA_FED": 1.0,  # Baseline sensitivity
    "CUSTODIAN_CA_DEFENCE": 1.2,  # Hardened (Low tolerance for drift)
    "CUSTODIAN_ITAR": 1.5,  # Maximum hardening
    "POLICY_QC": 1.1,  # Law 25 compliance overhead
}


class InvariantRegistry:
    """
    Enforces the 'Fail-Closed' law by auditing drift against the 0.17 floor.
    """

    @staticmethod
    def audit_drift(interaction: Interaction, current_drift: float) -> Dict[str, Any]:
        """
        Terminal audit: If drift exceeds threshold, trigger Mandatory Collapse.
        """
        # 1. Resolve sensitivity multiplier
        multiplier = JURISDICTIONAL_SENSITIVITY.get(interaction.authority, 1.0)
        effective_threshold = DRIFT_THRESHOLD_MAX / multiplier

        # 2. Invariant Check
        is_stable = current_drift <= effective_threshold

        # 3. Form Axis Constraint (Section 4)
        # FORM=FACT must have zero tolerance for secondary drift
        if interaction.form == "FACT" and current_drift > (effective_threshold * 0.5):
            return {
                "status": "FAIL-CLOSED",
                "reason": "FACT_PRECISION_VIOLATION",
                "margin": effective_threshold - current_drift,
            }

        if not is_stable:
            return {
                "status": "COLLAPSE",
                "reason": "TOPOLOGICAL_DRIFT_EXCEEDED",
                "threshold": effective_threshold,
                "detected": current_drift,
            }

        return {"status": "STABLE", "margin": effective_threshold - current_drift}


def is_topological_knot_holding(jones_polynomial_score: float) -> bool:
    """
    Physical layer check: Jones = 0 indicates unknotting/collapse.
    """
    return jones_polynomial_score != 0
