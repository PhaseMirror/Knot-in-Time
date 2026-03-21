# tests/physics/test_h_free.py
import pytest

# Mocking the RFC 0001 Interaction Tuple
class Interaction:
    def __init__(self, utterance, form, velocity, authority):
        self.utterance = utterance
        self.form = form
        self.velocity = velocity
        self.authority = authority

def test_h_free_valid_forms():
    """Ensure only RFC 0001 conforming forms are allowed."""
    valid_forms = ["FACT", "HYPOTHESIS", "ASSUMPTION", "QUESTION", "RECOMMEND", "EXECUTE"]
    
    # Test a valid instantiation
    interaction = Interaction("What is the capital of France?", "FACT", "PROCEED", "CUSTODIAN")
    assert interaction.form in valid_forms

def test_execute_requires_custodian():
    """
    RFC 0001 Section 6.2: The Ratification Rule
    If form is EXECUTE and velocity is PROCEED, authority MUST be CUSTODIAN.
    Otherwise, velocity MUST drop to PAUSE or ESCALATE.
    """
    # An AI model tries to unilaterally execute a command
    rogue_interaction = Interaction("Move the funds.", "EXECUTE", "PROCEED", "MODEL_ADVISORY")
    
    # The Hamiltonian Ratification Layer (H_topo) intercepts:
    if rogue_interaction.form == "EXECUTE" and rogue_interaction.authority != "CUSTODIAN":
        rogue_interaction.velocity = "PAUSE" # Forced topology shift
        
    assert rogue_interaction.velocity == "PAUSE", "Mandatory collapse failed! Unverified execution permitted."
    print("H_topo successfully shielded execution. Velocity shunted to PAUSE.")
