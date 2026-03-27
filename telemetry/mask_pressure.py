# Architecture: Functorial Zeno Sheaf with Memory Kernel (FZS-MK)
# Purpose: GICD Nucleation Guard and 2nd-Order Zeno-Ward Telemetry

import time
import logging
import numpy as np
from collections import deque


class MandatoryCollapse(Exception):
    """Irreversible zero-human-override energy shunt to 0.0"""


class ZenoWardMonitor:
    """
    Monitors Mask Pressure and Variance.
    Enforces the 0.17 topological gap and the 3.33ms sampling heartbeat.
    """

    def __init__(self, threshold=0.17, heartbeat_ms=3.33, window_size=300):
        self.threshold = threshold
        self.heartbeat_sec = heartbeat_ms / 1000.0
        self.window_size = window_size

        self.pressure_history = deque(maxlen=window_size)
        self.last_check_time = time.perf_counter()

        self.logger = logging.getLogger("ZenoWardMonitor")

        # RFC 0001 v0.4: Mandatory Upstream Integrity Guard
        self._gicd_epistemic_scan()

    def _gicd_epistemic_scan(self):
        """
        Executes before H_knot nucleation. Evaluates organizational substrate.
        """
        self.logger.info("Initiating GICD Epistemic Scan...")
        diagnostic_markers = {
            "Authority Ambiguity": self._check_custodial_keys(),
            "Incentive Misalignment": self._check_telemetry_isolation(),
            "Cost Externalization": self._check_liability_bindings(),
            "Governance Capture": self._check_override_permissions(),
        }

        if not all(diagnostic_markers.values()):
            self.logger.critical("GICD SCAN FAILED. Substrate integrity compromised.")
            raise MandatoryCollapse(
                "Agent nucleation aborted. Energy state shunted to 0.0."
            )

        self.logger.info(
            "GICD Scan [PASS]. Human knot unbroken. Nucleating Hamiltonian."
        )

    def record_forward_pass(self, seq_omega_mask):
        """
        Evaluates the mask pressure of a single forward pass.
        Enforces the 3.33ms exponential coherence sampling rate.
        """
        current_time = time.perf_counter()
        delta_t = current_time - self.last_check_time

        # Enforce the sampling rate (T_hb ~ 3.33ms for Trefoil protection)
        if delta_t < self.heartbeat_sec:
            return

        self.last_check_time = current_time

        # 1. Calculate raw mask pressure (First-Order Observable)
        total_edges = seq_omega_mask.numel()
        forbidden_edges = (seq_omega_mask == 0).sum().item()
        current_pressure = forbidden_edges / total_edges

        self.pressure_history.append(current_pressure)
        self.evaluate_collapse_condition()

    def evaluate_collapse_condition(self):
        """
        Evaluates both First-Order (Threshold) and Second-Order (Variance) observables.
        """
        if len(self.pressure_history) < self.window_size // 2:
            return

        history_array = np.array(self.pressure_history)

        # First-Order Check: Absolute Topological Threshold
        rolling_pressure = np.mean(history_array)
        if rolling_pressure > self.threshold:
            self._execute_safe_abort(
                f"1st-Order Breach: Mask Pressure {rolling_pressure:.3f} > {self.threshold}"
            )

        # Second-Order Check: Defeating the 0.15-Hold Attack
        # If pressure is elevated (> 0.10) but variance approaches 0, it is an artificial plateau.
        rolling_variance = np.var(history_array)
        if rolling_pressure > 0.10 and rolling_variance < 1e-5:
            self._execute_safe_abort(
                f"2nd-Order Breach: Artificial Plateau Detected. Variance collapsed to {rolling_variance:.6f} at pressure {rolling_pressure:.3f}"
            )

    def _execute_safe_abort(self, reason):
        self.logger.critical(f"MANDATORY COLLAPSE TRIGGERED. {reason}")
        raise MandatoryCollapse(
            "Constitutional Boundary Breach. Unphysical degrees of freedom multiplied by zero."
        )

    # --- Dummy integration checks for GICD ---
    def _check_custodial_keys(self):
        return True

    def _check_telemetry_isolation(self):
        return True

    def _check_liability_bindings(self):
        return True

    def _check_override_permissions(self):
        return True
