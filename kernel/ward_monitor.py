"""
Ward Monitor for FZS-MK Drift Detection

Implements the single authority for Ward residual computation W(t) = D_KL(ρ || ρ₀).
This replaces the duplicate drift metric in session_spectral_gate.py.

Reference: FZS-MK Blueprint §2.2
"""

import numpy as np
from typing import Tuple, Optional
from scipy.stats import entropy
from pirtm.sigma.kernel import MemoryKernelProtocol


class WardMonitor:
    """
    Single authority for drift monitoring via Ward residual.
    
    Computes KL divergence D_KL(ρ || ρ₀) where ρ₀ is the reference
    lawful manifold state. The residual must be monotone-decreasing
    under unperturbed evolution.
    """
    
    def __init__(
        self,
        reference_state: Optional[np.ndarray] = None,
        delta_operational: float = 0.10,
        smoothing_window: int = 5,
    ):
        """
        Initialize Ward monitor.
        
        Args:
            reference_state: ρ₀ reference state vector (lawful manifold)
            delta_operational: Operational threshold for drift detection
            smoothing_window: Window size for residual smoothing
        """
        self.reference_state = reference_state
        self.delta_operational = delta_operational
        self.smoothing_window = smoothing_window
        
        # History for monotone validation
        self.residual_history: list[float] = []
        self.state_history: list[np.ndarray] = []
    
    def compute_residual(self, current_state: np.ndarray) -> float:
        """
        Compute Ward residual W(t) = D_KL(ρ || ρ₀).
        
        Args:
            current_state: Current state vector ρ
        
        Returns:
            KL divergence from reference state (≥ 0)
        """
        if self.reference_state is None:
            # Use initial state as reference if not provided
            if len(self.state_history) == 0:
                self.reference_state = current_state.copy()
                return 0.0
            else:
                self.reference_state = self.state_history[0].copy()
        
        # Ensure states are probability distributions (normalize if needed)
        rho = self._normalize_to_distribution(current_state)
        rho0 = self._normalize_to_distribution(self.reference_state)
        
        # Compute KL divergence: D_KL(ρ || ρ₀)
        residual = entropy(rho, rho0)
        
        # Store in history for validation
        self.residual_history.append(residual)
        self.state_history.append(current_state.copy())
        
        # Apply smoothing if history is sufficient
        if len(self.residual_history) >= self.smoothing_window:
            smoothed = self._smooth_residuals()
            return smoothed[-1]  # Return most recent smoothed value
        
        return residual
    
    def _normalize_to_distribution(self, state: np.ndarray) -> np.ndarray:
        """
        Normalize state vector to probability distribution.
        
        Args:
            state: Raw state vector
        
        Returns:
            Normalized probability distribution
        """
        # Ensure non-negative
        state = np.maximum(state, 0)
        
        # Normalize to sum to 1
        total = np.sum(state)
        if total > 0:
            return state / total
        else:
            # Uniform distribution if all zeros
            return np.ones_like(state) / len(state)
    
    def _smooth_residuals(self) -> np.ndarray:
        """
        Apply moving average smoothing to residual history.
        
        Returns:
            Smoothed residual array
        """
        residuals = np.array(self.residual_history)
        window = np.ones(self.smoothing_window) / self.smoothing_window
        return np.convolve(residuals, window, mode='valid')
    
    def validate_monotonicity(
        self,
        tolerance: float = 1e-6
    ) -> Tuple[bool, str]:
        """
        Validate monotone-decreasing property of residuals.
        
        Args:
            tolerance: Allowed deviation from strict monotonicity
        
        Returns:
            (is_monotone: bool, diagnostic_message: str)
        """
        if len(self.residual_history) < 2:
            return True, "Insufficient history for monotonicity check"
        
        # Check if residuals are decreasing (diffs should be ≤ 0)
        smoothed = self._smooth_residuals() if len(self.residual_history) >= self.smoothing_window else self.residual_history
        diffs = np.diff(smoothed)
        violations = np.sum(diffs > tolerance)
        
        if violations == 0:
            max_violation = np.max(diffs) if len(diffs) > 0 else 0.0
            return True, f"✓ Monotone decreasing (max violation: {max_violation:.2e})"
        else:
            max_violation = np.max(diffs)
            return False, f"✗ Non-monotone at {violations} points (max violation: {max_violation:.2e})"
    
    def is_drift_detected(self) -> bool:
        """
        Check if operational drift threshold is exceeded.
        
        Returns:
            True if drift detected (residual > delta_operational)
        """
        if len(self.residual_history) == 0:
            return False
        
        current_residual = self.residual_history[-1]
        return current_residual > self.delta_operational
    
    def reset_history(self):
        """Reset residual and state history."""
        self.residual_history.clear()
        self.state_history.clear()
    
    def get_monitor_status(self) -> dict:
        """
        Get comprehensive monitor status for diagnostics.
        
        Returns:
            Dictionary with monitor state information
        """
        return {
            'residual_history_length': len(self.residual_history),
            'current_residual': self.residual_history[-1] if self.residual_history else 0.0,
            'drift_detected': self.is_drift_detected(),
            'monotonicity_valid': self.validate_monotonicity()[0],
            'delta_operational': self.delta_operational,
            'smoothing_window': self.smoothing_window,
        }