import numpy as np
import cmath

"""
Helix-Hamiltonian Invariants Registry v0.4 (Hardened)
Mathematical definitions for Jones and Alexander Polynomials 
evaluated at the RFC 0001 Standards Track points.
"""

# --- TOPOLOGICAL CONSTANTS ---
# 5th Root of Unity (k=3 SU(2) Chern-Simons level)
T_JONES = np.exp(2j * np.pi / 5) 

# Alexander Symmetry Point (The "Topological Surface Area" Point)
T_ALEX = -1.0

# --- GLOBAL COUPLING CONSTANTS (The "Hammy Stuff" Defaults) ---
KAPPA  = 1.25    # Substrate Stiffness (V_time strength)
OMEGA  = 50.0    # Quantum Drive Frequency (Intent processing)
GAMMA_CRITICAL = 1.0 # The Exceptional Point (Lambda-Turbulence Threshold)

# --- THE KNOT REGISTRY ---
# Mapping Knot Topology to its Physical/Governance Profile
# J_eval: |J(K)| at T_JONES
# A_eval: |Delta(K)| at T_ALEX
KNOT_REGISTRY = {
    "0_1": { # The Unknot (Pure Potential / Ungoverned)
        "name": "Unknot",
        "J_eval": 1.0,
        "A_eval": 1.0,
        "stability": "NONE"
    },
    "3_1": { # The Trefoil (The Sovereign AI Node)
        "name": "Trefoil",
        "J_eval": 1.618,  # The Golden Ratio (Topological Mass Gap)
        "A_eval": 3.0,    # 3-fold Symmetry (Narrow Spectral Lines)
        "stability": "RATIFIED"
    },
    "4_1": { # The Figure-Eight (Topological Gap / Silent Node)
        "name": "Figure-Eight",
        "J_eval": 0.0,    # Vanishing Point (KIMI Audit Case)
        "A_eval": 5.0,    # High complexity / Low line-width
        "stability": "SILENT"
    },
    "5_1": { # The Cinquefoil (High-Order Commonwealth Agent)
        "name": "Cinquefoil",
        "J_eval": 2.118,  # Increased Shield Strength
        "A_eval": 5.0,    # Robust to Substrate Wobble
        "stability": "ENHANCED"
    }
}

def get_shield_energy(knot_type="3_1"):
    """Returns the energy gap (lambda) based on Jones Invariance."""
    knot = KNOT_REGISTRY.get(knot_type, KNOT_REGISTRY["0_1"])
    return knot["J_eval"]

def get_spectral_limit(knot_type="3_1"):
    """Returns the dissipative line-width limit based on Alexander Invariance."""
    knot = KNOT_REGISTRY.get(knot_type, KNOT_REGISTRY["0_1"])
    # The Alexander Selection Rule: Im(omega) proportional to 1/Delta
    return 1.0 / knot["A_eval"]

def check_lambda_turbulence(gamma):
    """
    Checks if Advisory Intent (gamma) is approaching the Exceptional Point.
    Returns (True, "CRITICAL") if the system is about to unknot.
    """
    if gamma >= GAMMA_CRITICAL:
        return True, "CRITICAL"
    elif gamma >= 0.85 * GAMMA_CRITICAL:
        return False, "TURBULENT"
    return False, "LAMINAR"
