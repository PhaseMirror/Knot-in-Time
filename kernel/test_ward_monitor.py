"""
Unit Tests for Ward Monitor Component

Tests drift detection and monotonicity validation.
Critical: Validates monotone-descent property under synthetic data.
"""

import numpy as np
import pytest
from pirtm.sigma.core.zeno.ward_monitor import WardMonitor


class TestWardMonitor:
    """Test suite for WardMonitor implementation."""
    
    def test_monitor_initialization(self):
        """Test monitor parameter initialization."""
        monitor = WardMonitor(delta_operational=0.15, smoothing_window=3)
        
        assert monitor.delta_operational == 0.15
        assert monitor.smoothing_window == 3
        assert len(monitor.residual_history) == 0
    
    def test_residual_computation_basic(self):
        """Test basic residual computation."""
        monitor = WardMonitor()
        
        # Set reference state
        ref_state = np.array([0.5, 0.5])
        monitor.reference_state = ref_state
        
        # Test identical state (should give residual = 0)
        current_state = np.array([0.5, 0.5])
        residual = monitor.compute_residual(current_state)
        
        assert residual == 0.0
    
    def test_residual_different_states(self):
        """Test residual computation for different states."""
        monitor = WardMonitor()
        
        # Reference: uniform distribution
        ref_state = np.array([0.5, 0.5])
        monitor.reference_state = ref_state
        
        # Current: skewed distribution
        current_state = np.array([0.8, 0.2])
        residual = monitor.compute_residual(current_state)
        
        assert residual > 0.0  # KL divergence should be positive
    
    def test_auto_reference_initialization(self):
        """Test automatic reference state initialization."""
        monitor = WardMonitor()
        
        # First call should set reference and return 0
        state1 = np.array([0.6, 0.4])
        residual1 = monitor.compute_residual(state1)
        
        assert residual1 == 0.0
        np.testing.assert_array_equal(monitor.reference_state, state1)
    
    def test_normalization_to_distribution(self):
        """Test state vector normalization."""
        monitor = WardMonitor()
        
        # Raw state (not normalized)
        raw_state = np.array([2.0, 3.0])
        normalized = monitor._normalize_to_distribution(raw_state)
        
        assert np.isclose(np.sum(normalized), 1.0)
        assert np.all(normalized >= 0)
    
    def test_zero_state_normalization(self):
        """Test normalization of zero state (edge case)."""
        monitor = WardMonitor()
        
        zero_state = np.array([0.0, 0.0])
        normalized = monitor._normalize_to_distribution(zero_state)
        
        # Should become uniform distribution
        expected = np.array([0.5, 0.5])
        np.testing.assert_array_almost_equal(normalized, expected)
    
    def test_monotonicity_validation_sufficient_history(self):
        """Test monotonicity validation with sufficient history."""
        monitor = WardMonitor(smoothing_window=3)
        
        # Create decreasing residuals (good case)
        monitor.residual_history = [0.5, 0.4, 0.3, 0.2, 0.1]
        
        is_monotone, message = monitor.validate_monotonicity()
        assert is_monotone
        assert "✓" in message
    
    def test_monotonicity_validation_insufficient_history(self):
        """Test monotonicity validation with insufficient history."""
        monitor = WardMonitor()
        
        # Only one point
        monitor.residual_history = [0.5]
        
        is_monotone, message = monitor.validate_monotonicity()
        assert is_monotone  # Should pass due to insufficient data
        assert "Insufficient history" in message
    
    def test_monotonicity_validation_violation(self):
        """Test monotonicity validation with violations."""
        monitor = WardMonitor(smoothing_window=3)
        
        # Create increasing residuals (bad case)
        monitor.residual_history = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        is_monotone, message = monitor.validate_monotonicity()
        assert not is_monotone
        assert "✗" in message
        assert "Non-monotone" in message
    
    def test_drift_detection(self):
        """Test drift detection threshold."""
        monitor = WardMonitor(delta_operational=0.2)
        
        # Below threshold
        monitor.residual_history = [0.1]
        assert not monitor.is_drift_detected()
        
        # Above threshold
        monitor.residual_history = [0.3]
        assert monitor.is_drift_detected()
    
    def test_smoothing_application(self):
        """Test residual smoothing."""
        monitor = WardMonitor(smoothing_window=3)
        
        # Add residuals that need smoothing
        residuals = [0.1, 0.2, 0.3, 0.4, 0.5]
        monitor.residual_history = residuals.copy()  # Set directly to avoid extra calls
        
        # With 5 points and window=3, should get smoothed values
        smoothed = monitor._smooth_residuals()
        expected_length = len(residuals) - monitor.smoothing_window + 1  # 5 - 3 + 1 = 3
        assert len(smoothed) == expected_length
        
        # Smoothed values should be averages
        expected_first = (0.1 + 0.2 + 0.3) / 3
        assert np.isclose(smoothed[0], expected_first)
    
    def test_reset_history(self):
        """Test history reset functionality."""
        monitor = WardMonitor()
        
        # Add some history
        monitor.compute_residual(np.array([0.5, 0.5]))
        monitor.compute_residual(np.array([0.6, 0.4]))
        
        assert len(monitor.residual_history) > 0
        
        # Reset
        monitor.reset_history()
        
        assert len(monitor.residual_history) == 0
        assert len(monitor.state_history) == 0
    
    def test_monitor_status(self):
        """Test monitor status reporting."""
        monitor = WardMonitor(delta_operational=0.1)
        
        # Add some data
        monitor.compute_residual(np.array([0.5, 0.5]))
        monitor.compute_residual(np.array([0.6, 0.4]))
        
        status = monitor.get_monitor_status()
        
        required_keys = [
            'residual_history_length',
            'current_residual',
            'drift_detected',
            'monotonicity_valid',
            'delta_operational',
            'smoothing_window'
        ]
        
        for key in required_keys:
            assert key in status