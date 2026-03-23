"""
Helix Hamiltonian - Consensus (v0.4 Federation)
Enforces the Jones Invariant Consensus across verified peers.
"""

from typing import List, Dict, Any
from ..core import Interaction

class LatticeConsensus:
    """
    Synchronizes the 'Fail-Closed' state across the federated lattice.
    Ensures that 0.17 drift violations propagate as mandatory refusals.
    """

    def __init__(self, node_sync: Any):
        self.node_sync = node_sync
        self.threshold = 0.17

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
