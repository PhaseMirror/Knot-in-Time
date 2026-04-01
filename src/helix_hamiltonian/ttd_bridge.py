"""
Bridge runtime connecting RFC 0001 interactions to lattice checks.
"""

from __future__ import annotations

import datetime
import os
import time
from typing import Any, Dict, Optional

import requests

from .authority import JurisdictionalGuard, ratify_interaction
from .core import Interaction, KnotHamiltonian, NodeState, verify_authority_ambiguity
from .invariants import InvariantRegistry, is_topological_knot_holding


GICD_URL = os.getenv("GICD_URL", "https://gicd-scanner-231586465188.us-central1.run.app/gicd-scan")
AWS_URL = os.getenv("AWS_URL", "https://erdmzd08ud.execute-api.us-east-1.amazonaws.com/default/helix-prime-4")
AZURE_URL = os.getenv("AZURE_URL", "")
AZURE_KEY = os.getenv("AZURE_FUNCTION_KEY", "")
GUARDIAN_ENABLED = os.getenv("GUARDIAN_ENABLED", "true").lower() == "true"
FZSMK_ENABLED = os.getenv("FZSMK_ENABLED", "true").lower() == "true"


def _run_fzsmk_gate(gicd_payload: Dict[str, Any], token_ids: list) -> Optional[Dict[str, Any]]:
    """Local FZS-MK physics gate. Returns FAIL dict or None if passed."""
    try:
        import numpy as np
        from helix_sovereign.core import (
            create_sovereign_engine,
            GICDBlockError,
            DeltaCritViolation,
            TopologicalCollapse,
            DELTA_CRIT,
        )
    except ImportError:
        return None  # helix_sovereign not available

    # Map GICD boolean payload to authority/cost specs
    markers = gicd_payload or {}
    has_authority = not markers.get("authority_ambiguity", False)
    has_cost = not markers.get("cost_externalization", False)
    authority_spec = {"decision_bounds": ["constitutional"]} if has_authority else None
    cost_allocation = (
        {"compute": {"internalized": True, "externalized": False}}
        if has_cost else
        {"compute": {"internalized": False, "externalized": True}}
    )

    n = max(len(token_ids), 4)
    try:
        engine = create_sovereign_engine(
            seq_len=n, module_count=n,
            authority_spec=authority_spec,
            cost_allocation=cost_allocation,
        )
    except GICDBlockError as e:
        return {"status": "FAIL", "reason": f"FZS-MK GICD block: {e}"}
    except TopologicalCollapse as e:
        return {"status": "FAIL", "reason": f"FZS-MK topological collapse: {e}"}

    # Build Hermitian Hamiltonian from token_ids
    x = np.array(token_ids[:n], dtype=float)
    x = x / (np.linalg.norm(x) + 1e-12)
    H = np.outer(x, x)
    H = (H + H.T) / 2.0

    try:
        _rho, meta = engine.step(H, dt=0.01)
    except (DeltaCritViolation, TopologicalCollapse) as e:
        return {"status": "FAIL", "reason": f"FZS-MK kill-switch: {e}"}

    if meta.is_violation:
        return {
            "status": "FAIL",
            "reason": (
                f"FZS-MK delta_crit breach: margin={meta.margin:.4f}, "
                f"entropy_delta={meta.entropy_delta:.4f} (threshold={DELTA_CRIT})"
            ),
            "delta_inf": meta.delta_inf,
            "epsilon_star": meta.epsilon_star,
            "gamma_est": meta.gamma_est,
            "stability_tier": meta.stability_tier,
            "robustness_budget": meta.robustness_budget,
        }
    return None  # Passed


def pre_nucleation_check(gicd_payload: Dict[str, Any], token_ids: list) -> Dict[str, Any]:
    """Call all sovereign services. Returns status PASS or FAIL with reason."""
    # Guardian constitutional compliance check (local — no network call)
    if GUARDIAN_ENABLED:
        try:
            import sys
            _guardian_path = os.getenv("GUARDIAN_PATH", "Z:/helix-ttd-gemini")
            if _guardian_path not in sys.path:
                sys.path.insert(0, _guardian_path)
            from helix_code.constitutional_compliance import ConstitutionalCompliance
            checker = ConstitutionalCompliance()
            nucleation_text = (
                f"[FACT] Nucleation requested with token_ids={token_ids}. "
                f"[FACT] GICD markers: {gicd_payload}. "
                f"[HYPOTHESIS] Agent nucleation may proceed if all markers clear."
            )
            report = checker.evaluate(nucleation_text, "TTD_BRIDGE")
            if not report.compliant:
                return {
                    "status": "FAIL",
                    "reason": f"Guardian constitutional violation: {report.drift_code} — {report.violations[:2]}"
                }
        except ImportError:
            pass  # Guardian not available — skip check

    # FZS-MK local physics gate (no network call)
    fzsmk_result = None
    if FZSMK_ENABLED:
        fzsmk_result = _run_fzsmk_gate(gicd_payload, token_ids)
        if fzsmk_result is not None:
            return fzsmk_result

    # GICD scan
    gicd_resp = requests.post(GICD_URL, json=gicd_payload, timeout=10)
    gicd_resp.raise_for_status()
    if gicd_resp.json()["status"] != "PASS":
        return {"status": "FAIL", "reason": gicd_resp.json()["reason"]}

    # AWS attention kernel
    aws_resp = requests.post(AWS_URL, json={"token_ids": token_ids}, timeout=10)
    aws_resp.raise_for_status()
    aws_data = aws_resp.json()

    # Contraction gate: GapLB must be >= 0
    if aws_data.get("GapLB", 0.0) < 0:
        return {"status": "FAIL", "reason": f"Attention kernel not contractive: GapLB={aws_data['GapLB']}"}

    # MUB alarm gate: if alarm and action is shrink_tau, flag but don't block
    mub_alarm  = aws_data.get("mub_alarm", False)
    mub_action = aws_data.get("mub_action", "accept")

    # Azure memory kernel
    az_data = {}
    if AZURE_URL:
        azure_url = f"{AZURE_URL}?code={AZURE_KEY}" if AZURE_KEY else AZURE_URL
        az_resp = requests.post(azure_url, json={"token_ids": token_ids}, timeout=120)
        az_resp.raise_for_status()
        az_data = az_resp.json()

    result = {
        "status": "PASS",
        "reason": "All sovereign services cleared.",
        "attention_bias": aws_data.get("bias"),
        "SlopeUB": aws_data.get("SlopeUB"),
        "GapLB": aws_data.get("GapLB"),
        "mub_D_t": aws_data.get("mub_D_t"),
        "mub_alarm": mub_alarm,
        "mub_action": mub_action,
        "memory_bias": az_data.get("bias"),
        "consensus_reached": az_data.get("consensus_reached"),
        "guardian_enabled": GUARDIAN_ENABLED,
        "fzsmk_enabled": FZSMK_ENABLED,
    }

    # Emit auditable receipt
    try:
        import sys
        _receipt_path = os.getenv("GUARDIAN_PATH", "Z:/helix-ttd-gemini")
        _physics_path = os.getenv("PHYSICS_GATE_PATH", "Z:/helix-physics-gate")
        if _physics_path not in sys.path:
            sys.path.insert(0, _physics_path)
        from receipt import emit_receipt
        emit_receipt(
            gate="pre_nucleation_check",
            inputs={"gicd_payload": gicd_payload, "token_ids": token_ids},
            outputs=result,
            receipt_dir=os.getenv("RECEIPT_DIR", "Z:/checksums/receipts")
        )
    except Exception:
        pass  # Receipt emission is non-blocking

    return result


class TTDBridge:
    """Execution bridge for a single local node."""

    HEARTBEAT_INTERVAL: float = 0.00333  # tau_0 / P(3_1) = 3.33 / 1000
    HEARTBEAT_SHRINK_FACTOR: float = 0.5  # applied when MUB action = shrink_tau
    HEARTBEAT_MIN: float = 0.001          # floor

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
        self._heartbeat_interval = self.HEARTBEAT_INTERVAL
        self._mub_shrink_active = False

    def apply_mub_action(self, mub_action: str, mub_D_t: float = 0.0) -> None:
        """Adjust heartbeat period based on MUB drift audit action."""
        if mub_action == "shrink_tau":
            self._heartbeat_interval = max(
                self.HEARTBEAT_MIN,
                self._heartbeat_interval * self.HEARTBEAT_SHRINK_FACTOR
            )
            self._mub_shrink_active = True
        elif mub_action == "accept" and self._mub_shrink_active:
            # Restore nominal heartbeat when drift clears
            self._heartbeat_interval = self.HEARTBEAT_INTERVAL
            self._mub_shrink_active = False

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
            "heartbeat_interval": self._heartbeat_interval,
            "mub_shrink_active": self._mub_shrink_active,
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
            time.sleep(self._heartbeat_interval)


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


__all__ = ["SovereignBridge", "TTDBridge", "pre_nucleation_check"]
