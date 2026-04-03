"""
FZS-MK Kernel Composition

Composes MemoryKernel, WardMonitor, and ZenoProjector into a unified
FZSKernel that implements the complete Functorial-Zeno-Sheaf-with-Memory-Kernel.

Reference: FZS-MK Blueprint §4
"""

import numpy as np
from typing import Dict, Any
from pirtm.sigma.kernel import MemoryKernelProtocol
from pirtm.sigma.core.zeno.memory_kernel import MemoryKernel
from pirtm.sigma.core.zeno.ward_monitor import WardMonitor
from pirtm.sigma.core.zeno.zeno_projector import ZenoProjector


class FZSKernel(MemoryKernelProtocol):
    """
    Complete FZS-MK implementation composing all components.
    
    This kernel provides the full memory-weighted constraint layer
    that governs phase mirror dissonance correction.
    """
    
    def __init__(
        self,
        memory_kernel: MemoryKernel,
        ward_monitor: WardMonitor,
        zeno_projector: ZenoProjector,
    ):
        """
        Initialize FZS kernel with composed components.
        
        Args:
            memory_kernel: MemoryKernel instance for history convolution
            ward_monitor: WardMonitor instance for drift detection
            zeno_projector: ZenoProjector instance for state correction
        """
        self.memory_kernel = memory_kernel
        self.ward_monitor = ward_monitor
        self.zeno_projector = zeno_projector
        
        # Track application statistics
        self.application_count = 0
        self.correction_count = 0
    
    @classmethod
    def create_default(cls) -> 'FZSKernel':
        """
        Create FZS kernel with default component configurations.
        
        Returns:
            Configured FZSKernel instance
        """
        # Default configurations per blueprint
        memory_kernel = MemoryKernel(
            alpha=0.1,      # Decay rate
            omega=2.0,      # Oscillation frequency
            phi=0.0,        # Phase offset
            time_scale=1.0  # Normalization scale
        )
        
        ward_monitor = WardMonitor(
            delta_operational=0.10,  # Operational threshold
            smoothing_window=5       # Residual smoothing
        )
        
        zeno_projector = ZenoProjector(
            ward_monitor=ward_monitor,
            epsilon=0.05,           # Regularization parameter
            max_iterations=100,     # Optimization limit
            tolerance=1e-6          # Convergence tolerance
        )
        
        return cls(memory_kernel, ward_monitor, zeno_projector)
    
    def convolve(self, t: float, history: np.ndarray) -> np.ndarray:
        """
        Apply K(t, τ) convolution over session history.
        
        Delegates to MemoryKernel component.
        """
        return self.memory_kernel.convolve(t, history)
    
    def ward_residual(self, rho: np.ndarray, rho0: np.ndarray) -> float:
        """
        Compute W(t) = D_KL(rho || rho0).
        
        Delegates to WardMonitor component.
        """
        # Set reference state if not already set
        if self.ward_monitor.reference_state is None:
            self.ward_monitor.reference_state = rho0
        
        return self.ward_monitor.compute_residual(rho)
    
    def zeno_project(self, rho: np.ndarray, epsilon: float = 0.05) -> np.ndarray:
        """
        Continuous projection toward lawful manifold.
        
        Delegates to ZenoProjector component.
        """
        self.application_count += 1
        
        projected = self.zeno_projector.project_state(rho)
        
        # Check if significant correction occurred
        residual_before = self.ward_monitor.compute_residual(rho)
        residual_after = self.ward_monitor.compute_residual(projected)
        
        if residual_after < residual_before * 0.9:  # 10% improvement threshold
            self.correction_count += 1
        
        return projected
    
    def apply_constraint(self, session_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply FZS-MK constraint to session payload.
        
        This is the main integration point for the hybrid kernel session.
        Applies memory-weighted correction to prevent phase mirror dissonance.
        
        Args:
            session_payload: Current session state payload
        
        Returns:
            Constrained payload with applied corrections
        """
        # Extract state vector from payload (assuming 'state' key exists)
        if 'state' not in session_payload:
            # If no state key, pass through unchanged
            return session_payload
        
        current_state = np.array(session_payload['state'])
        
        # Apply Zeno projection
        corrected_state = self.zeno_project(current_state)
        
        # Update payload with corrected state
        constrained_payload = session_payload.copy()
        constrained_payload['state'] = corrected_state.tolist()
        constrained_payload['fzs_applied'] = True
        constrained_payload['fzs_residual'] = self.ward_monitor.compute_residual(corrected_state)
        
        return constrained_payload
    
    def get_kernel_status(self) -> Dict[str, Any]:
        """
        Get comprehensive kernel status for diagnostics.
        
        Returns:
            Dictionary with kernel state information
        """
        return {
            'application_count': self.application_count,
            'correction_count': self.correction_count,
            'correction_rate': self.correction_count / max(self.application_count, 1),
            'memory_kernel': self.memory_kernel.get_kernel_properties(),
            'ward_monitor': self.ward_monitor.get_monitor_status(),
            'zeno_projector': self.zeno_projector.get_projection_diagnostics(),
        }
    
    def reset_statistics(self):
        """Reset application and correction counters."""
        self.application_count = 0
        self.correction_count = 0
        self.ward_monitor.reset_history()
        self.zeno_projector.reset_history()