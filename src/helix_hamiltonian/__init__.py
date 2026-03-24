"""Public package surface for helix_hamiltonian."""

__version__ = "1.0.1"

from .authority import (
    AuthorityLevel,
    JurisdictionalGuard,
    ratify_interaction,
    ratify_velocity,
)
from .core import Interaction, KnotHamiltonian, NodeState
from .policy_compiler import PolicyCompiler
from .ttd_bridge import SovereignBridge, TTDBridge

__all__ = [
    "AuthorityLevel",
    "Interaction",
    "JurisdictionalGuard",
    "KnotHamiltonian",
    "NodeState",
    "PolicyCompiler",
    "SovereignBridge",
    "TTDBridge",
    "__version__",
    "ratify_interaction",
    "ratify_velocity",
]
