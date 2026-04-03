"""
Memory Kernel Implementation for FZS-MK

Implements the log-periodic convolution K(t, τ) over session history.
This is the core non-Markovian memory weighting mechanism.

Reference: FZS-MK Blueprint §2.1
"""

import numpy as np
from typing import Optional
from pirtm.sigma.kernel import MemoryKernelProtocol


class MemoryKernel(MemoryKernelProtocol):
    """
    Log-periodic memory kernel for history-weighted state propagation.
    
    Implements K(t, τ) = exp(-α log(t/τ)) * cos(ω log(t/τ) + φ)
    where α controls decay rate, ω controls oscillation frequency,
    and φ is the phase offset.
    """
    
    def __init__(
        self,
        alpha: float = 0.1,
        omega: float = 2.0,
        phi: float = 0.0,
        time_scale: float = 1.0,
    ):
        """
        Initialize memory kernel parameters.
        
        Args:
            alpha: Decay rate parameter (controls memory persistence)
            omega: Oscillation frequency (log-periodic modulation)
            phi: Phase offset for kernel modulation
            time_scale: Characteristic time scale for normalization
        """
        self.alpha = alpha
        self.omega = omega
        self.phi = phi
        self.time_scale = time_scale
        
        # Pre-compute kernel normalization
        self._kernel_norm = self._compute_kernel_norm()
    
    def convolve(self, t: float, history: np.ndarray) -> np.ndarray:
        """
        Apply K(t, τ) convolution over session history.
        
        Args:
            t: Current time (normalized)
            history: Session history array of shape (n_timesteps, state_dim)
        
        Returns:
            Weighted state vector at time t
        """
        if history.size == 0:
            raise ValueError("History cannot be empty")
        
        n_timesteps, state_dim = history.shape
        weights = np.zeros(n_timesteps)
        
        # Compute kernel weights for each historical timestep
        for i, tau in enumerate(np.linspace(0.1, t, n_timesteps)):
            if tau > 0:  # Avoid log(0)
                log_ratio = np.log(t / tau)
                weights[i] = np.exp(-self.alpha * log_ratio) * \
                           np.cos(self.omega * log_ratio + self.phi)
        
        # Normalize weights
        weights = weights / (np.sum(np.abs(weights)) + 1e-8)
        
        # Apply convolution: weighted sum over history
        result = np.sum(weights[:, np.newaxis] * history, axis=0)
        
        return result
    
    def _compute_kernel_norm(self) -> float:
        """
        Compute kernel normalization constant for stability.
        
        Returns:
            Normalization factor
        """
        # Numerical integration of kernel over typical time range
        t_vals = np.linspace(0.1, 10.0, 1000)
        kernel_vals = np.exp(-self.alpha * np.log(t_vals)) * \
                     np.cos(self.omega * np.log(t_vals) + self.phi)
        
        return np.trapezoid(np.abs(kernel_vals), t_vals)
    
    def get_kernel_properties(self) -> dict:
        """
        Get kernel parameter summary for diagnostics.
        
        Returns:
            Dictionary of kernel properties
        """
        return {
            'alpha': self.alpha,
            'omega': self.omega,
            'phi': self.phi,
            'time_scale': self.time_scale,
            'normalization': self._kernel_norm,
            'memory_persistence': 1.0 / self.alpha,  # Characteristic decay time
        }