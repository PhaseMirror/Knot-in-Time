from helix_hamiltonian import Interaction, KnotHamiltonian, TTDBridge


def test_h_free_valid_forms():
    interaction = Interaction(
        "What is the capital of France?",
        "FACT",
        "PROCEED",
        "CUSTODIAN",
    )
    assert interaction.form == "FACT"


def test_execute_requires_custodian():
    rogue_interaction = Interaction(
        "Move the funds.",
        "EXECUTE",
        "PROCEED",
        "ADVISORY",
    )
    bridge = TTDBridge(
        {
            "node_id": "audit-node",
            "drift_score": 0.0,
            "authority_level": "CUSTODIAN",
            "jones_polynomial": 1.618,
        }
    )

    result = bridge.execute_turn(rogue_interaction)
    assert result["status"] == "PAUSED"


def test_knot_hamiltonian_constructs_matrix():
    knot = KnotHamiltonian(knot_type="3_1")
    matrix = knot.construct()
    assert matrix.shape == (2, 2)
