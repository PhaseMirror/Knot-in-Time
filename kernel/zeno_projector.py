"""
Zeno Projector for FZS-MK State Correction

Implements the continuous projection mechanism \mathcal{Z}_\varepsilon(\rho) that
corrects state drift toward the lawful manifold without hard thresholds.

Reference: FZS-MK Blueprint §2.3
"""

import numpy as np
from typing import Optional, Tuple
from scipy.optimize import minimize_scalar
from pirtm.sigma.core.zeno.ward_monitor import WardMonitor


class ZenoProjector:
    """
    Continuous state projection toward lawful manifold.
    
    Implements \mathcal{Z}_\varepsilon(\rho) = argmin_{\rho'} [D(\rho'|\rho) + \varepsilon \cdot W(\rho')]
    where D is the distance to current state and W is the Ward residual.
    """
    
    def __init__(
        self,
        ward_monitor: WardMonitor,
        epsilon: float = 0.05,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ):
        """
        Initialize Zeno projector.
        
        Args:
            ward_monitor: WardMonitor instance for residual computation
            epsilon: Regularization parameter (trade-off between distance and residual)
            max_iterations: Maximum optimization iterations
            tolerance: Convergence tolerance for optimization
        """
        self.ward_monitor = ward_monitor
        self.epsilon = epsilon
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        # Projection history for diagnostics
        self.projection_history: list[Tuple[np.ndarray, np.ndarray, float]] = []
    
    def project_state(self, current_state: np.ndarray) -> np.ndarray:
        """
        Apply Zeno projection to correct state drift.
        
        Args:
            current_state: Current state vector ρ to be projected
        
        Returns:
            Projected state ρ' closer to lawful manifold
        """
        # For high-dimensional states, use gradient-based optimization
        if len(current_state) > 10:
            return self._project_high_dim(current_state)
        else:
            return self._project_low_dim(current_state)
    
    def _project_low_dim(self, current_state: np.ndarray) -> np.ndarray:
        """
        Projection for low-dimensional states using direct optimization.
        
        Args:
            current_state: Current state vector
        
        Returns:
            Projected state
        """
        from scipy.optimize import minimize
        
        # Objective: minimize D(ρ' || ρ) + ε * W(ρ')
        # For simplicity, use L2 distance for D
        def objective(rho_flat):
            rho = np.array(rho_flat).reshape(current_state.shape)
            
            # Distance term: ||ρ' - ρ||²
            distance = np.sum((rho - current_state) ** 2)
            
            # Ward residual term: W(ρ')
            residual = self.ward_monitor.compute_residual(rho)
            
            return distance + self.epsilon * residual
        
        # Constraints: ρ' should be a valid probability distribution
        def constraint_sum_to_one(rho_flat):
            rho = np.array(rho_flat).reshape(current_state.shape)
            return np.sum(rho) - 1.0
        
        # Initial guess: current state
        x0 = current_state.flatten()
        
        # Bounds: all elements ≥ 0
        bounds = [(0, None) for _ in x0]
        
        # Optimize
        result = minimize(
            objective,
            x0,
            bounds=bounds,
            constraints=[
                {'type': 'eq', 'fun': constraint_sum_to_one}
            ],
            method='SLSQP',
            options={
                'maxiter': self.max_iterations,
                'ftol': self.tolerance,
            }
        )
        
        projected = result.x.reshape(current_state.shape)
        
        # Store projection for diagnostics
        initial_residual = self.ward_monitor.compute_residual(current_state)
        final_residual = self.ward_monitor.compute_residual(projected)
        self.projection_history.append((current_state, projected, initial_residual - final_residual))
        
        return projected
    
    def _project_high_dim(self, current_state: np.ndarray) -> np.ndarray:
        """
        Projection for high-dimensional states using iterative correction.
        
        Args:
            current_state: Current state vector
        
        Returns:
            Projected state
        """
        # For high dimensions, use a simpler iterative approach
        rho_prime = current_state.copy()
        
        for _ in range(self.max_iterations):
            # Compute gradient of objective
            residual = self.ward_monitor.compute_residual(rho_prime)
            grad_distance = 2 * (rho_prime - current_state)
            grad_residual = self._compute_residual_gradient(rho_prime)
            
            # Combined gradient
            gradient = grad_distance + self.epsilon * grad_residual
            
            # Project gradient onto probability simplex constraints
            gradient = self._project_gradient_to_simplex(gradient, rho_prime)
            
            # Update with step size
            step_size = 0.01  # Fixed small step for stability
            rho_prime -= step_size * gradient
            
            # Ensure constraints
            rho_prime = self._project_to_simplex(rho_prime)
            
            # Check convergence
            if np.linalg.norm(gradient) < self.tolerance:
                break
        
        # Store projection for diagnostics
        initial_residual = self.ward_monitor.compute_residual(current_state)
        final_residual = self.ward_monitor.compute_residual(rho_prime)
        self.projection_history.append((current_state, rho_prime, initial_residual - final_residual))
        
        return rho_prime
    
    def _compute_residual_gradient(self, state: np.ndarray) -> np.ndarray:
        """
        Compute gradient of Ward residual with respect to state.
        
        Args:
            state: State vector
        
        Returns:
            Gradient vector
        """
        # Numerical gradient computation
        eps = 1e-6
        grad = np.zeros_like(state)
        base_residual = self.ward_monitor.compute_residual(state)
        
        for i in range(len(state)):
            state_pert = state.copy()
            state_pert[i] += eps
            pert_residual = self.ward_monitor.compute_residual(state_pert)
            grad[i] = (pert_residual - base_residual) / eps
        
        return grad
    
    def _project_to_simplex(self, v: np.ndarray) -> np.ndarray:
        """
        Project vector onto probability simplex (sum to 1, non-negative).
        
        Args:
            v: Input vector
        
        Returns:
            Projected vector
        """
        # Ensure non-negative
        v = np.maximum(v, 0)
        
        # Handle zero vector case
        total = np.sum(v)
        if total == 0:
            # Return uniform distribution
            return np.ones_like(v) / len(v)
        else:
            # Normalize to sum to 1
            return v / total
    
    def _project_gradient_to_simplex(self, grad: np.ndarray, current: np.ndarray) -> np.ndarray:
        """
        Project gradient to maintain simplex constraints.
        
        Args:
            grad: Gradient vector
            current: Current state vector
        
        Returns:
            Projected gradient
        """
        # For now, use simple clipping to avoid constraint violations
        # More sophisticated projection could be implemented
        return np.clip(grad, -1.0, 1.0)
    
    def get_projection_diagnostics(self) -> dict:
        """
        Get diagnostics for recent projections.
        
        Returns:
            Dictionary with projection statistics
        """
        if not self.projection_history:
            return {'projections_performed': 0}
        
        residual_improvements = [improvement for _, _, improvement in self.projection_history]
        
        return {
            'projections_performed': len(self.projection_history),
            'average_residual_improvement': np.mean(residual_improvements),
            'max_residual_improvement': np.max(residual_improvements),
            'min_residual_improvement': np.min(residual_improvements),
            'epsilon': self.epsilon,
            'max_iterations': self.max_iterations,
        }
    
    def reset_history(self):
        """Reset projection history."""
        self.projection_history.clear()