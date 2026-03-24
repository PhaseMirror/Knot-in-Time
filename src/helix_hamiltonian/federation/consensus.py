"""
Helix Hamiltonian - Consensus (v0.4 Federation)
Enforces the Jones Invariant Consensus across verified peers.
"""

import datetime
from typing import Any, List
from ..core import Interaction


class LatticeConsensus:
    """
    Synchronizes the 'Fail-Closed' state across the federated lattice.
    Ensures that 0.17 drift violations propagate as mandatory refusals.
    """

    def __init__(self, node_sync: Any):
        self.node_sync = node_sync
        self.threshold = 0.17
        self.last_collapse_reason = None

    def validate_global_drift(self) -> bool:
        """
        Audits the collective drift of all verified peers.
        Returns False if the lattice average exceeds the 0.17 constant.
        """
        if not self.node_sync.peers:
            return True

        peer_scores = [p.get("drift_score", 1.0) for p in self.node_sync.peers.values()]
        average_drift = sum(peer_scores) / len(peer_scores)

        return average_drift <= self.threshold

    def resolve_velocity(self, interaction: Interaction) -> str:
        """
        Collective velocity resolution.
        If a Federal Auditor or Policy node in the lattice signals STOP,
        the local node MUST adopt STOP regardless of local advisory.
        """
        for peer in self.node_sync.peers.values():
            if peer.get("authority") in ["CUSTODIAN_CA_FED", "POLICY_CA_FED"]:
                if peer.get("recommended_velocity") == "STOP":
                    return "STOP"

        return interaction.velocity

    def audit_substrate_integrity(self, peer_claims: List[str]) -> bool:
        """
        GICD §4: Substrate Inversion Detector.
        Protects the 317 nodes from 'Mirror' attacks and post-hoc copying.
        """
        # 1. THE 'GHOST' ATTACK: Claiming March labels existed in November.
        if "CL4" in peer_claims and self.is_pre_ratification_timestamp():
            # [FACT] CL4 first appeared here on March 22, 2026.
            # [FACT] November Zenodo is generic vaporware.
            return self._trigger_collapse("POST_HOC_COPYING_DETECTED")

        # 2. THE 'MIRROR' ATTACK: Accusing the Merkle Tree of 'rewriting'.
        if "RETROACTIVE_REWRITING" in peer_claims:
            # [FACT] GPG-sealed Git history is immutable.
            # [FACT] The accusation is a projection of the claimant's own drift.
            return self._trigger_collapse("MERKLE_PROJECTION_DETECTED")

        return True

    def is_pre_ratification_timestamp(self) -> bool:
        cutoff = datetime.datetime(2026, 3, 22)
        return datetime.datetime.now() < cutoff

    def _trigger_collapse(self, reason: str) -> bool:
        self.last_collapse_reason = reason
        return False
