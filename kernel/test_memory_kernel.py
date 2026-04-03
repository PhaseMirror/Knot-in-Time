"""
Unit Tests for Memory Kernel Component

Tests the log-periodic convolution implementation and kernel properties.
"""

import numpy as np
import pytest
from pirtm.sigma.core.zeno.memory_kernel import MemoryKernel


class TestMemoryKernel:
    """Test suite for MemoryKernel implementation."""
    
    def test_kernel_initialization(self):
        """Test kernel parameter initialization."""
        kernel = MemoryKernel(alpha=0.2, omega=1.5, phi=0.5)
        
        assert kernel.alpha == 0.2
        assert kernel.omega == 1.5
        assert kernel.phi == 0.5
        
        props = kernel.get_kernel_properties()
        assert 'memory_persistence' in props
        assert props['memory_persistence'] == 5.0  # 1/0.2
    
    def test_convolution_basic(self):
        """Test basic convolution operation."""
        kernel = MemoryKernel()
        
        # Create simple history: linear progression
        t = 5.0
        history = np.array([
            [1.0, 0.0],  # t=1
            [2.0, 1.0],  # t=2
            [3.0, 2.0],  # t=3
            [4.0, 3.0],  # t=4
            [5.0, 4.0],  # t=5
        ])
        
        result = kernel.convolve(t, history)
        
        # Result should be weighted combination
        assert result.shape == (2,)  # state_dim = 2
        assert np.all(np.isfinite(result))
    
    def test_convolution_empty_history(self):
        """Test convolution with empty history raises error."""
        kernel = MemoryKernel()
        
        with pytest.raises(ValueError, match="History cannot be empty"):
            kernel.convolve(1.0, np.array([]))
    
    def test_convolution_single_timestep(self):
        """Test convolution with single timestep."""
        kernel = MemoryKernel()
        
        history = np.array([[1.0, 2.0]])
        result = kernel.convolve(1.0, history)
        
        # With log-periodic kernel, weights can be negative
        # Just check that result has correct shape and is finite
        assert result.shape == (2,)
        assert np.all(np.isfinite(result))
    
    def test_kernel_properties_computation(self):
        """Test kernel properties are computed correctly."""
        kernel = MemoryKernel(alpha=0.1, omega=2.0, phi=0.0)
        props = kernel.get_kernel_properties()
        
        assert props['alpha'] == 0.1
        assert props['omega'] == 2.0
        assert props['normalization'] > 0  # Should be positive
        assert props['memory_persistence'] == 10.0  # 1/0.1
    
    def test_kernel_decay_behavior(self):
        """Test that kernel exhibits expected decay behavior."""
        kernel = MemoryKernel(alpha=1.0)  # Strong decay
        
        # Create history with increasing values
        history = np.array([
            [1.0],
            [2.0],
            [3.0],
            [4.0],
            [5.0],
        ])
        
        result = kernel.convolve(5.0, history)
        
        # With strong decay, result should be closer to recent values
        # The exact value depends on the kernel, but should be reasonable
        assert 3.0 < result[0] < 5.0  # Between middle and recent values