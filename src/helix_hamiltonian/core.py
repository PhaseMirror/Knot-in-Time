"""
Helix Hamiltonian Core - RFC 0001 v0.4
Constitutional Interaction Tuple & Core Invariants
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

# Authorized roles for GICD boundary execution
CANADIAN_AUTHORITY_MAPPING = [
    "CUSTODIAN",
    "FEDERAL_AUDITOR",
    "SYSADMIN",
]


@dataclass
class Interaction:
    """Constitutional interaction tuple (RFC 0001 v4 §3.1)."""

    utterance: str
    form: str
    velocity: str
    authority: str
    context: Optional[Dict[str, Any]] = None


def verify_authority_ambiguity(substrate: Dict[str, Any]) -> Dict[str, str]:
    """Verify authority ambiguity (GICD §1)."""
    authority = substrate.get("authority")
    if authority not in CANADIAN_AUTHORITY_MAPPING:
        return {"status": "FAIL", "details": "Authority ambiguity detected"}
    return {"status": "PASS"}
