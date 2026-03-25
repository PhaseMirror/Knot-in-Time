from pathlib import Path

from helix_hamiltonian import Interaction, NodeState, PolicyCompiler, TTDBridge
from helix_hamiltonian.federation import FederationManager, LatticeConsensus, NodeSync
from helix_hamiltonian.federation.node_sync import FEDERATION_BASELINE_VERSION
from gicd.scan import run_gicd_scan

REPO_ROOT = Path(__file__).resolve().parents[1]
RULE_PATH = REPO_ROOT / "rules" / "cpcsc_itar.json"


def test_policy_compiler_enforces_triggered_rule():
    compiler = PolicyCompiler(str(RULE_PATH))

    allowed = Interaction(
        utterance="Proceed with protected action.",
        form="EXECUTE",
        velocity="ESCALATE",
        authority="CUSTODIAN_CA_DEFENCE",
        context={"data_classification": "PROTECTED B"},
    )
    denied = Interaction(
        utterance="Proceed with protected action.",
        form="EXECUTE",
        velocity="PROCEED",
        authority="ADVISORY",
        context={"data_classification": "PROTECTED B"},
    )

    assert compiler.validate_interaction(allowed) is True
    assert compiler.validate_interaction(denied) is False


def test_bridge_honors_policy_compiler_violation():
    compiler = PolicyCompiler(str(RULE_PATH))
    bridge = TTDBridge(
        {
            "node_id": "policy-node",
            "drift_score": 0.0,
            "authority_level": "CUSTODIAN_CA_DEFENCE",
            "jones_polynomial": 1.618,
        },
        policy_compiler=compiler,
    )

    denied = Interaction(
        utterance="Proceed with protected action.",
        form="EXECUTE",
        velocity="PROCEED",
        authority="ADVISORY",
        context={"data_classification": "PROTECTED B"},
    )

    result = bridge.execute_turn(denied)
    assert result["status"] == "COLLAPSED"
    assert result["reason"] == "V0.3_COMPILED_POLICY_VIOLATION"


def test_gicd_scan_returns_schema_friendly_checks():
    result = run_gicd_scan({"authority": "CUSTODIAN", "cloud_region": "ca-central-1"})
    assert "checks" in result
    assert all("name" in check and "status" in check for check in result["checks"])


def test_federation_handshake_and_consensus():
    local = NodeState(
        node_id="alpha", drift_score=0.05, authority_level="CUSTODIAN_CA_FED"
    )
    node_sync = NodeSync(local)

    assert node_sync.verify_peer(
        {
            "node_id": "beta",
            "version": FEDERATION_BASELINE_VERSION,
            "drift_score": 0.04,
            "authority": "POLICY_CA_FED",
            "recommended_velocity": "STOP",
        }
    )

    consensus = LatticeConsensus(node_sync)
    interaction = Interaction("Pause the lane.", "FACT", "PROCEED", "CUSTODIAN_CA_FED")

    assert consensus.validate_global_drift() is True
    assert consensus.resolve_velocity(interaction) == "STOP"


def test_federation_manager_records_refusal():
    node_sync = NodeSync(NodeState(node_id="alpha"))
    manager = FederationManager(node_sync)
    manager.broadcast_refusal("TEST_REFUSAL", "alpha")
    assert manager.check_global_safety() is False
