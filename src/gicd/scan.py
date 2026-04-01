"""Backward-compatibility shim — canonical module is helix_hamiltonian.gicd.scan."""

from helix_hamiltonian.gicd.scan import *  # noqa: F401,F403
from helix_hamiltonian.gicd.scan import run_gicd_scan  # explicit for test import
