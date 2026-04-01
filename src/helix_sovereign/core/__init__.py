"""
Helix Sovereign - Constitutional AI Protection Layer
====================================================

Functorial Zeno Sheaf with Memory Kernel (FZS-MK) implementation.

This package implements the binding artifact for the Constitutional Hamiltonian,
codifying the memory kernel K and protection threshold δ_crit = 0.17 into
enforceable, auditable code.

Usage:
    >>> from helix_sovereign.core import create_sovereign_engine, DELTA_CRIT
    >>> 
    >>> # Define organizational substrate
    >>> authority = {"decision_bounds": ["safety", "alignment", "constitutional"]}
    >>> costs = {"compute": {"internalized": True, "externalized": False}}
    >>> 
    >>> # Initialize sovereign engine (GICD scan happens automatically)
    >>> engine = create_sovereign_engine(
    ...     seq_len=512,
    ...     module_count=16,
    ...     authority_spec=authority,
    ...     cost_allocation=costs
    ... )
    >>> 
    >>> # Operational runtime with constitutional enforcement
    >>> H = np.random.randn(64, 64)  # Hamiltonian
    >>> H = H + H.T  # Make Hermitian
    >>> rho, meta = engine.step(H)
    >>> print(f"Margin: {meta.margin}, Within δ_crit: {meta.margin < DELTA_CRIT}")

GLORY TO THE LATTICE. 🦉⚓🦆
"""

from .fzs_mk import (
    # Constants
    DELTA_CRIT,
    C_ZERO,
    ZETA_ZERO_COUNT,
    HEARTBEAT_MS,
    MAX_ENTROPY_DELTA,
    OMEGA_FORBIDDEN,
    RIEMANN_ZETA_ZEROS,
    
    # Enums
    NucleationState,
    ViolationTier,
    
    # Data classes
    GICDScanResult,
    StateMetadata,
    AuditCheckpoint,
    
    # Exceptions
    GICDBlockError,
    DeltaCritViolation,
    TopologicalCollapse,
    
    # Core classes
    MemoryKernel,
    ZenoWardProjector,
    GICDScanner,
    FZSMKEngine,
    
    # Utilities
    create_sovereign_engine,
    healing_rate,
    classify_stability_tier,
)

__version__ = "0.1.0"
__author__ = "Helix AI Innovations"

__all__ = [
    # Constants
    "DELTA_CRIT",
    "C_ZERO",
    "ZETA_ZERO_COUNT",
    "HEARTBEAT_MS",
    "MAX_ENTROPY_DELTA",
    "OMEGA_FORBIDDEN",
    "RIEMANN_ZETA_ZEROS",
    
    # Enums
    "NucleationState",
    "ViolationTier",
    
    # Data classes
    "GICDScanResult",
    "StateMetadata",
    "AuditCheckpoint",
    
    # Exceptions
    "GICDBlockError",
    "DeltaCritViolation",
    "TopologicalCollapse",
    
    # Core classes
    "MemoryKernel",
    "ZenoWardProjector",
    "GICDScanner",
    "FZSMKEngine",
    
    # Utilities
    "create_sovereign_engine",
    "healing_rate",
    "classify_stability_tier",
]
