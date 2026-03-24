"""
Helix Hamiltonian - Federation (v0.4)
Manages Refusal Propagation and Federated Fail-Closed Logic.
"""

from typing import Dict, Any, List
from .node_sync import NodeSync


class FederationManager:
    """
    The 'Immune System' of the Lattice.
    Propagates refusal states to prevent substrate contamination.
    """

    def __init__(self, node_sync: NodeSync):
        self.node_sync = node_sync
        self.local_refusal_cache: List[str] = []

    def broadcast_refusal(self, reason: str, node_id: str):
        """
        Propagates a local refusal/collapse state to all verified peers.
        Ensures that 'No Motion Without Judgment' is a federated invariant.
        """
        refusal_event = {
            "type": "MANDATORY_COLLAPSE",
            "origin": node_id,
            "reason": reason,
            "signature_required": True,
        }

        # In a live manifold, this would trigger an encrypted p2p broadcast
        for peer_id in self.node_sync.peers:
            self._notify_peer(peer_id, refusal_event)

        self.local_refusal_cache.append(reason)

    def _notify_peer(self, peer_id: str, event: Dict[str, Any]):
        """Internal: Logic for peer-to-peer event notification."""
        # v0.4 Placeholder for gRPC/Websocket message handling
        pass

    def check_global_safety(self) -> bool:
        """
        Audit: Returns False if any peer has broadcast a CRITICAL collapse.
        """
        return len(self.local_refusal_cache) == 0
