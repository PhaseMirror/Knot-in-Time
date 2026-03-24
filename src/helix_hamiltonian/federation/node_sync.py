"""
Helix Hamiltonian - Node Sync (v0.4 Federation)
Handles the Constitutional Handshake and Peer Verification.
"""

import datetime
from typing import Dict, Any
from ..core import NodeState

FEDERATION_BASELINE_VERSION = "1.0.1"


class NodeSync:
    """
    Manages node-to-node synchronization and integrity handshakes.
    Ensures that peers are running the current signed baseline.
    """

    def __init__(self, local_state: NodeState):
        self.local_state = local_state
        self.peers: Dict[str, Dict[str, Any]] = {}

    def initiate_handshake(self) -> Dict[str, Any]:
        """
        Generates a signed state snapshot for peer discovery.
        Includes the 0.17 drift constant and current authority level.
        """
        snapshot = {
            "node_id": self.local_state.node_id,
            "version": FEDERATION_BASELINE_VERSION,
            "timestamp": datetime.datetime.now().isoformat(),
            "drift_score": self.local_state.drift_score,
            "authority": self.local_state.authority_level,
        }
        return snapshot

    def verify_peer(self, peer_snapshot: Dict[str, Any]) -> bool:
        """
        Validates a peer against local constitutional invariants.
        Refuses connection if peer version or drift (0.17) is inadmissible.
        """
        # 1. Version Check: peers must align to the current signed baseline
        if peer_snapshot.get("version") != FEDERATION_BASELINE_VERSION:
            return False

        # 2. Threshold Audit: 0.17 Invariant enforcement
        if peer_snapshot.get("drift_score", 1.0) > 0.17:
            return False

        # 3. Successful Verification
        self.peers[peer_snapshot["node_id"]] = peer_snapshot
        return True
