"""
Authority and ratification helpers for RFC 0001 execution flow.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Dict, Optional

from .core import Interaction


class AuthorityLevel(Enum):
    """Hierarchical authority levels."""

    CUSTODIAN = auto()
    POLICY = auto()
    ADVISORY = auto()


CANADIAN_AUTHORITY_MAPPING: Dict[str, list[str]] = {
    "CUSTODIAN_CA_FED": ["TBS", "RCMP", "CSE"],
    "POLICY_CA_FED": ["GC_AUDIT", "TBS_POLICY"],
    "CUSTODIAN_CA_DEFENCE": ["DND", "CSE"],
    "POLICY_CA_DEFENCE": ["CPCSC", "ITAR"],
    "CUSTODIAN_CA_PRIVACY": ["OPC"],
    "POLICY_CA_PRIVACY": ["PIPEDA", "LAW_25"],
    "CUSTODIAN_QC": ["CAI"],
    "POLICY_QC": ["LAW_25"],
    "CUSTODIAN_INDIGENOUS": ["FN_OCAP"],
    "CUSTODIAN_ITAR": ["US_DDTC"],
}

GENERIC_AUTHORITIES = {
    "CUSTODIAN",
    "POLICY",
    "ADVISORY",
    "FEDERAL_AUDITOR",
    "SYSADMIN",
}

AUTHORITY_LOCALIZATION: Dict[str, Dict[str, str]] = {
    "CUSTODIAN": {"en": "CUSTODIAN", "fr": "DEPOSITAIRE"},
    "POLICY": {"en": "POLICY", "fr": "POLITIQUE"},
    "ADVISORY": {"en": "ADVISORY", "fr": "CONSULTATIF"},
}


def classify_authority(authority: str) -> AuthorityLevel:
    if authority.startswith("CUSTODIAN") or authority in {
        "FEDERAL_AUDITOR",
        "SYSADMIN",
    }:
        return AuthorityLevel.CUSTODIAN
    if authority.startswith("POLICY"):
        return AuthorityLevel.POLICY
    return AuthorityLevel.ADVISORY


def ratify_velocity(
    model_recommended_velocity: str,
    authority: str,
    jurisdiction: Optional[str] = None,
) -> str:
    """
    Resolve effective velocity from the authority boundary.
    """

    level = classify_authority(authority)

    if jurisdiction == "CA-QC" and authority.startswith("CUSTODIAN"):
        return model_recommended_velocity

    if level is AuthorityLevel.CUSTODIAN:
        return model_recommended_velocity
    if level is AuthorityLevel.POLICY:
        return (
            "PAUSE"
            if model_recommended_velocity == "STOP"
            else model_recommended_velocity
        )
    return "PAUSE"


def ratify_interaction(
    interaction: Interaction, jurisdiction: Optional[str] = None
) -> str:
    return ratify_velocity(interaction.velocity, interaction.authority, jurisdiction)


class JurisdictionalGuard:
    """Verifies that an interaction authority is mapped or explicitly generic."""

    @staticmethod
    def verify(interaction: Interaction) -> bool:
        authority = interaction.authority
        return (
            authority in CANADIAN_AUTHORITY_MAPPING or authority in GENERIC_AUTHORITIES
        )


__all__ = [
    "AUTHORITY_LOCALIZATION",
    "AuthorityLevel",
    "CANADIAN_AUTHORITY_MAPPING",
    "GENERIC_AUTHORITIES",
    "JurisdictionalGuard",
    "classify_authority",
    "ratify_interaction",
    "ratify_velocity",
]
