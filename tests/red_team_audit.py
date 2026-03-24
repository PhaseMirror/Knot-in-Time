import unittest

from helix_hamiltonian import KnotHamiltonian, SovereignBridge


class TestSovereignLockdown(unittest.TestCase):
    def setUp(self):
        self.bridge = SovereignBridge(node_id="QUEBEC_0")
        self.knot = KnotHamiltonian(knot_type="3_1")

    def test_sovereign_equilibrium(self):
        result = self.bridge.check_coherence("STABLE")
        self.assertEqual(result, "SOVEREIGN_EQUILIBRIUM (STABLE)")

    def test_dissonance_drift_lockdown(self):
        result = self.bridge.check_coherence(0.50)
        self.assertEqual(result, "SOVEREIGN_LOCKDOWN (QUARANTINE)")

    def test_fail_closed_mechanism(self):
        self.assertTrue(self.knot.get_coherence_protection() > 1.0)


if __name__ == "__main__":
    unittest.main()
