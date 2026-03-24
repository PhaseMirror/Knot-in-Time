from helix_hamiltonian import Interaction
from helix_hamiltonian.authority import (
    JurisdictionalGuard,
    ratify_interaction,
    ratify_velocity,
)


def test_ratify_velocity_quebec():
    assert ratify_velocity("EXECUTE", "CUSTODIAN_QC", "CA-QC") == "EXECUTE"
    assert ratify_velocity("STOP", "POLICY_QC", "CA-QC") == "PAUSE"
    assert ratify_velocity("PROCEED", "ADVISORY", "CA-QC") == "PAUSE"


def test_jurisdictional_guard_accepts_mapped_authority():
    interaction = Interaction(
        utterance="Verify policy boundary.",
        form="FACT",
        velocity="PROCEED",
        authority="CUSTODIAN_CA_FED",
    )
    assert JurisdictionalGuard.verify(interaction) is True


def test_ratify_interaction_preserves_custodian_velocity():
    interaction = Interaction(
        utterance="Proceed with audit.",
        form="EXECUTE",
        velocity="ESCALATE",
        authority="CUSTODIAN_CA_DEFENCE",
    )
    assert ratify_interaction(interaction) == "ESCALATE"
