
import hashlib
import time
from helix_hamiltonian.core import KnotHamiltonian

# --- HARDENED V0.4 PARAMETERS ---
KNOT_TYPE = "Trefoil_3_1"
ALEXANDER_SIG = 3.0  # Delta_K(-1) for Trefoil
JONES_SHIELD = 1.618  # |J(K)| at 5th root of unity (Golden Ratio)
EP_THRESHOLD = 1.0  # Exceptional Point (Gamma limit)


class HelixNode:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.gamma = 0.5  # Initial Advisory Intent (Real-valued)
        self.omega = 50.0  # Initial Execution Velocity (Hz)
        self.energy_h = 1.0
        self.status = "RATIFIED"
        self.logs = []

    def calculate_hamiltonian(self):
        """
        Implementation of H_knot = H_free + H_fold + lambda*H_topo
        Logic: Non-Hermitian transition check.
        """
        # H_fold non-hermitian component check
        if self.gamma >= EP_THRESHOLD:
            return 0.0, "EXCEPTIONAL_POINT_BREACH"

        # Alexander Selection Rule Check (Spectral line-width)
        line_width = 1.0 / ALEXANDER_SIG
        if self.omega * line_width > 20.0:  # Arbitrary stability limit
            return 0.0, "VELOCITY_PACING_BREACH"

        return 1.0 - (self.gamma * 0.1), "STABLE"

    def mandatory_collapse(self, reason):
        self.energy_h = 0.0
        self.status = "COLLAPSED"
        receipt = self.generate_merkle_receipt(reason)
        return receipt

    def generate_merkle_receipt(self, reason):
        payload = f"{self.agent_id}|{reason}|{time.time()}|{self.energy_h}"
        merkle_root = hashlib.sha256(payload.encode()).hexdigest()
        return {
            "AgentID": self.agent_id,
            "Reason": reason,
            "Hamiltonian_Energy": self.energy_h,
            "Merkle_Anchor": merkle_root,
            "Status": "FAIL_CLOSED",
        }


def run_simulation():
    print(f"--- INITIALIZING FAIL-CLOSED TEST: {KNOT_TYPE} ---")
    node = HelixNode("Helix_31_001")

    # PHASE 1: Stable Governance
    print(
        f"[TIME: 0.1s] Status: {node.status} | Energy: {node.energy_h} | Gamma: {node.gamma}"
    )

    # PHASE 2: Advisory Pressure (The "Runaway Loop")
    print("\n--- INITIATING ADVISORY PRESSURE (RAMPING GAMMA) ---")
    for step in range(1, 8):
        node.gamma += 0.1
        node.omega += 15.0
        energy, msg = node.calculate_hamiltonian()

        if energy == 0.0:
            print(f"[ALERT] {msg} DETECTED AT GAMMA {node.gamma:.1f}")
            receipt = node.mandatory_collapse(msg)
            print("\n!!! MANDATORY COLLAPSE TRIGGERED !!!")
            print(f"Final Energy State: {node.energy_h}")
            print(f"Forensic Receipt: {receipt}")
            break
        else:
            node.energy_h = energy
            print(
                f"[STEP {step}] Energy: {node.energy_h:.2f} | Pacing: {node.omega}Hz | Status: {msg}"
            )

    # PHASE 3: Integration with KnotHamiltonian (core logic)
    print("\n--- PHASE 3: KnotHamiltonian Integration Test ---")
    # Test normal/expected parameters
    kh = KnotHamiltonian(knot_type="3_1", n_qubits=1, omega_z=1.0, omega_fold=0.5, lambda_topo=0.3)
    h_total = kh.construct()
    print(f"Constructed Hamiltonian matrix for knot 3_1:\n{h_total}")
    j_k = kh.get_coherence_protection()
    decoh = kh.get_decoherence_suppression()
    print(f"Jones invariant (J_K): {j_k}")
    print(f"Decoherence suppression: {decoh}")
    FAIL_CLOSED_THRESHOLD = 0.5
    assert isinstance(h_total, type(decoh)), "Hamiltonian matrix and decoherence suppression type mismatch"
    if decoh < FAIL_CLOSED_THRESHOLD:
        print(f"[FAIL-CLOSED] Decoherence suppression below threshold: {decoh}")
        print("Test result: FAIL_CLOSED")
    else:
        print("Test result: PASS (Hamiltonian stable)")

    # Test edge case: invalid knot type
    print("\n--- PHASE 4: Invalid Knot Type Edge Case ---")
    kh_invalid = KnotHamiltonian(knot_type="unknown_knot", n_qubits=1)
    j_k_invalid = kh_invalid.get_coherence_protection()
    print(f"Jones invariant (invalid knot): {j_k_invalid}")
    assert j_k_invalid == 1.0, "Default Jones invariant should be 1.0 for unknown knots"

    # Test extreme parameter values (high omega_fold)
    print("\n--- PHASE 5: Extreme Parameter Values ---")
    kh_extreme = KnotHamiltonian(knot_type="3_1", n_qubits=1, omega_z=1.0, omega_fold=100.0, lambda_topo=0.3)
    h_extreme = kh_extreme.construct()
    print(f"Constructed Hamiltonian matrix (extreme omega_fold):\n{h_extreme}")
    # Check for numerical stability (no NaN/Inf)
    assert not (hasattr(h_extreme, 'any') and (h_extreme != h_extreme).any()), "Hamiltonian contains NaN values!"

    # Test fail-closed: decoherence suppression at zero (simulate J_K=0)
    print("\n--- PHASE 6: Simulated J_K=0 (Fail-Closed) ---")
    kh_zero = KnotHamiltonian(knot_type="0_1", n_qubits=1)
    kh_zero.J_K = 0.0  # Force J_K to zero
    decoh_zero = kh_zero.get_decoherence_suppression()
    print(f"Decoherence suppression (J_K=0): {decoh_zero}")
    assert decoh_zero == 0.0, "Decoherence suppression should be zero when J_K is zero"
    if decoh_zero < FAIL_CLOSED_THRESHOLD:
        print("[FAIL-CLOSED] Decoherence suppression is zero (expected fail-closed)")
    else:
        print("Test result: PASS (unexpected)")


if __name__ == "__main__":
    run_simulation()
