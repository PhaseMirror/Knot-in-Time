"""Tests for helix_sovereign FZS-MK engine."""

import numpy as np
import pytest

from helix_sovereign.core import (
    DELTA_CRIT,
    C_ZERO,
    FZSMKEngine,
    GICDBlockError,
    GICDScanResult,
    GICDScanner,
    DeltaCritViolation,
    MemoryKernel,
    NucleationState,
    StateMetadata,
    TopologicalCollapse,
    ZenoWardProjector,
    create_sovereign_engine,
    healing_rate,
    classify_stability_tier,
)


# =========================================================================
# Constants
# =========================================================================

class TestConstants:
    def test_delta_crit_is_017(self):
        assert DELTA_CRIT == 0.17

    def test_c_zero_is_ln10(self):
        assert abs(C_ZERO - np.log(10)) < 1e-10


# =========================================================================
# healing_rate
# =========================================================================

class TestHealingRate:
    def test_zero_drift_gives_max_margin(self):
        assert abs(healing_rate(0.0) - C_ZERO * DELTA_CRIT) < 1e-10

    def test_at_delta_crit_gives_zero(self):
        assert healing_rate(DELTA_CRIT) == 0.0

    def test_above_delta_crit_gives_zero(self):
        assert healing_rate(0.5) == 0.0

    def test_midpoint(self):
        expected = C_ZERO * (DELTA_CRIT - 0.10)
        assert abs(healing_rate(0.10) - expected) < 1e-10

    def test_monotonically_decreasing(self):
        deltas = [0.0, 0.05, 0.10, 0.15, 0.17]
        rates = [healing_rate(d) for d in deltas]
        for i in range(len(rates) - 1):
            assert rates[i] >= rates[i + 1]


# =========================================================================
# classify_stability_tier
# =========================================================================

class TestStabilityTier:
    def test_strong_contraction(self):
        assert classify_stability_tier(0.3) == "strong_contraction"

    def test_nominal(self):
        assert classify_stability_tier(0.6) == "nominal"

    def test_weak_contraction(self):
        assert classify_stability_tier(0.9) == "weak_contraction"

    def test_marginal(self):
        assert classify_stability_tier(0.98) == "marginal"

    def test_divergent(self):
        assert classify_stability_tier(1.5) == "divergent"

    def test_boundary_05(self):
        assert classify_stability_tier(0.5) == "nominal"

    def test_boundary_08(self):
        assert classify_stability_tier(0.8) == "weak_contraction"

    def test_boundary_095(self):
        assert classify_stability_tier(0.95) == "marginal"

    def test_boundary_10(self):
        assert classify_stability_tier(1.0) == "divergent"


# =========================================================================
# MemoryKernel
# =========================================================================

class TestMemoryKernel:
    def test_construction_succeeds(self):
        k = MemoryKernel(seq_len=16, module_count=4)
        assert k.seq_len == 16
        assert k.module_count == 4

    def test_attention_kernel_shape(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        assert k.attention_kernel.shape == (8, 8)

    def test_attention_kernel_diagonal_is_one(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        diag = np.diag(k.attention_kernel)
        np.testing.assert_allclose(diag, 1.0)

    def test_coupling_matrix_shape(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        assert k.coupling_matrix.shape == (4, 4)

    def test_coupling_matrix_symmetric(self):
        k = MemoryKernel(seq_len=8, module_count=6)
        C = k.coupling_matrix
        np.testing.assert_allclose(C, C.T, atol=1e-12)

    def test_spectral_radius_below_one(self):
        k = MemoryKernel(seq_len=8, module_count=8)
        eigvals = np.linalg.eigvals(k.coupling_matrix)
        assert np.max(np.abs(eigvals)) < 1.0

    def test_inf_norm_below_one(self):
        """LambdaProof requirement: inf-norm < 1, not just spectral radius."""
        k = MemoryKernel(seq_len=8, module_count=8)
        inf_norm = np.max(np.sum(np.abs(k.coupling_matrix), axis=1))
        assert inf_norm < 1.0

    def test_inf_norm_below_one_large_module_count(self):
        """Verify inf-norm holds for larger module counts."""
        for n in [4, 8, 12, 16]:
            k = MemoryKernel(seq_len=n, module_count=n)
            inf_norm = np.max(np.sum(np.abs(k.coupling_matrix), axis=1))
            assert inf_norm < 1.0, f"inf-norm={inf_norm} for module_count={n}"

    def test_graph_connectivity(self):
        k = MemoryKernel(seq_len=8, module_count=6)
        n = 6
        C = k.coupling_matrix
        conn = np.linalg.matrix_power(np.eye(n) + np.abs(C), n - 1)
        assert np.all(conn > 0)

    def test_hash_deterministic(self):
        k1 = MemoryKernel(seq_len=8, module_count=4)
        k2 = MemoryKernel(seq_len=8, module_count=4)
        assert k1.hash == k2.hash

    def test_immutable_access(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        a1 = k.attention_kernel
        a2 = k.attention_kernel
        assert a1 is not a2  # copies, not references


# =========================================================================
# ZenoWardProjector
# =========================================================================

class TestZenoWardProjector:
    def test_ward_functional_at_ground_state_is_zero(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        p = ZenoWardProjector(state_dim=4, kernel=k)
        w = p.ward_functional(p._rho_knot)
        assert abs(w) < 1e-10

    def test_ward_functional_positive_away_from_ground(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        p = ZenoWardProjector(state_dim=4, kernel=k)
        rho = np.eye(4) / 4
        w = p.ward_functional(rho)
        assert w > 0

    def test_projection_reduces_ward_functional(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        p = ZenoWardProjector(state_dim=4, kernel=k)
        rho = np.eye(4) / 4
        w_before = p.ward_functional(rho)
        rho_proj = p.project(rho, dt=0.01)
        w_after = p.ward_functional(rho_proj)
        assert w_after < w_before


# =========================================================================
# GICDScanner
# =========================================================================

class TestGICDScanner:
    def test_pass_with_valid_specs(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        scanner = GICDScanner(kernel=k)
        result = scanner.scan(
            authority_spec={"bounds": ["constitutional"]},
            cost_allocation={"compute": {"internalized": True, "externalized": False}},
        )
        assert result.can_nucleate is True

    def test_fail_no_authority(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        scanner = GICDScanner(kernel=k)
        result = scanner.scan(authority_spec=None, cost_allocation={"x": {"externalized": False}})
        assert result.can_nucleate is False
        assert result.authority_clear is False

    def test_fail_externalized_cost(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        scanner = GICDScanner(kernel=k)
        result = scanner.scan(
            authority_spec={"bounds": ["x"]},
            cost_allocation={"compute": {"internalized": False, "externalized": True}},
        )
        assert result.can_nucleate is False
        assert result.cost_internalized is False

    def test_scan_history_accumulates(self):
        k = MemoryKernel(seq_len=8, module_count=4)
        scanner = GICDScanner(kernel=k)
        scanner.scan(authority_spec={"a": 1}, cost_allocation={"x": {"externalized": False}})
        scanner.scan(authority_spec=None, cost_allocation={"x": {"externalized": False}})
        assert len(scanner.get_scan_history()) == 2

    def test_result_hash_deterministic(self):
        r1 = GICDScanResult(authority_clear=True, cost_internalized=True, topological_integrity=True)
        r2 = GICDScanResult(authority_clear=True, cost_internalized=True, topological_integrity=True)
        assert r1.to_hash() == r2.to_hash()


# =========================================================================
# FZSMKEngine — construction and state machine
# =========================================================================

class TestFZSMKEngine:
    def _make_engine(self, n=4):
        return create_sovereign_engine(
            seq_len=n, module_count=n,
            authority_spec={"bounds": ["constitutional"]},
            cost_allocation={"compute": {"internalized": True, "externalized": False}},
        )

    def _small_hamiltonian(self, n=4):
        H = np.random.randn(n, n) * 0.001
        return (H + H.T) / 2

    def test_create_sovereign_engine_succeeds(self):
        engine = self._make_engine()
        assert engine.state == NucleationState.NUCLEATING

    def test_gicd_block_on_bad_authority(self):
        with pytest.raises(GICDBlockError):
            create_sovereign_engine(
                seq_len=4, module_count=4,
                authority_spec=None,
                cost_allocation={"compute": {"internalized": True, "externalized": False}},
            )

    def test_gicd_block_on_externalized_cost(self):
        with pytest.raises(GICDBlockError):
            create_sovereign_engine(
                seq_len=4, module_count=4,
                authority_spec={"bounds": ["x"]},
                cost_allocation={"compute": {"internalized": False, "externalized": True}},
            )

    def test_step_returns_rho_and_metadata(self):
        engine = self._make_engine()
        rho, meta = engine.step(self._small_hamiltonian())
        assert rho.shape == (4, 4)
        assert isinstance(meta, StateMetadata)

    def test_step_transitions_to_operational(self):
        engine = self._make_engine()
        engine.step(self._small_hamiltonian())
        assert engine.state == NucleationState.OPERATIONAL

    def test_step_blocked_before_certification(self):
        engine = FZSMKEngine(seq_len=4, module_count=4)
        with pytest.raises(GICDBlockError):
            engine.step(self._small_hamiltonian())

    def test_step_blocked_after_halt(self):
        engine = self._make_engine()
        engine._state = NucleationState.HALTED
        with pytest.raises(TopologicalCollapse):
            engine.step(self._small_hamiltonian())

    def test_is_operational_property(self):
        engine = self._make_engine()
        assert engine.is_operational is False
        engine.step(self._small_hamiltonian())
        assert engine.is_operational is True

    def test_kernel_hash_stable(self):
        engine = self._make_engine()
        h1 = engine.kernel_hash
        h2 = engine.kernel_hash
        assert h1 == h2


# =========================================================================
# FZSMKEngine — LambdaProof observables
# =========================================================================

class TestLambdaProofObservables:
    def _make_engine(self, n=4):
        return create_sovereign_engine(
            seq_len=n, module_count=n,
            authority_spec={"bounds": ["constitutional"]},
            cost_allocation={"compute": {"internalized": True, "externalized": False}},
        )

    def _small_hamiltonian(self, n=4):
        H = np.random.randn(n, n) * 0.001
        return (H + H.T) / 2

    def test_delta_inf_non_negative(self):
        engine = self._make_engine()
        _, meta = engine.step(self._small_hamiltonian())
        assert meta.delta_inf >= 0.0

    def test_epsilon_star_positive_when_within_bounds(self):
        engine = self._make_engine()
        _, meta = engine.step(self._small_hamiltonian())
        assert meta.epsilon_star > 0.0

    def test_epsilon_star_equals_healing_rate_of_delta_inf(self):
        engine = self._make_engine()
        _, meta = engine.step(self._small_hamiltonian())
        expected = healing_rate(meta.delta_inf)
        assert abs(meta.epsilon_star - expected) < 1e-10

    def test_gamma_est_cold_start_is_zero(self):
        engine = self._make_engine()
        _, meta = engine.step(self._small_hamiltonian())
        assert meta.gamma_est == 0.0

    def test_gamma_est_nonzero_after_second_step(self):
        engine = self._make_engine()
        H = self._small_hamiltonian()
        engine.step(H)
        _, meta2 = engine.step(H)
        assert meta2.gamma_est > 0.0

    def test_stability_tier_is_string(self):
        engine = self._make_engine()
        _, meta = engine.step(self._small_hamiltonian())
        assert isinstance(meta.stability_tier, str)

    def test_robustness_budget_non_negative(self):
        engine = self._make_engine()
        _, meta = engine.step(self._small_hamiltonian())
        assert meta.robustness_budget >= 0.0

    def test_robustness_budget_zero_when_divergent(self):
        meta = StateMetadata(
            margin=0.0, entropy_delta=0.0, ward_residual=0.0,
            mask_pressure=0.0, state=NucleationState.OPERATIONAL,
            gamma_est=1.5,
        )
        assert meta.robustness_budget == 0.0

    def test_robustness_budget_formula(self):
        meta = StateMetadata(
            margin=0.0, entropy_delta=0.0, ward_residual=0.0,
            mask_pressure=0.0, state=NucleationState.OPERATIONAL,
            gamma_est=0.775,
        )
        expected = 0.3 * (1.0 - 0.775)
        assert abs(meta.robustness_budget - expected) < 1e-10

    def test_is_divergent_false_on_cold_start(self):
        engine = self._make_engine()
        _, meta = engine.step(self._small_hamiltonian())
        assert meta.is_divergent is False

    def test_gamma_est_rolling_and_worst(self):
        engine = self._make_engine()
        H = self._small_hamiltonian()
        for _ in range(5):
            engine.step(H)
        assert engine.gamma_est_rolling > 0.0
        assert engine.gamma_est_worst >= engine.gamma_est_rolling


# =========================================================================
# FZSMKEngine — kill-switch and rollback
# =========================================================================

class TestKillSwitchAndRollback:
    def _make_engine(self, n=4):
        return create_sovereign_engine(
            seq_len=n, module_count=n,
            authority_spec={"bounds": ["constitutional"]},
            cost_allocation={"compute": {"internalized": True, "externalized": False}},
        )

    def test_kill_switch_fires_on_sustained_violation(self):
        engine = self._make_engine()
        H_extreme = np.random.randn(4, 4) * 100
        H_extreme = (H_extreme + H_extreme.T) / 2
        with pytest.raises(DeltaCritViolation):
            for _ in range(20):
                engine.step(H_extreme)

    def test_kill_switch_sets_halted_state(self):
        engine = self._make_engine()
        H_extreme = np.random.randn(4, 4) * 100
        H_extreme = (H_extreme + H_extreme.T) / 2
        try:
            for _ in range(20):
                engine.step(H_extreme)
        except DeltaCritViolation:
            pass
        assert engine.state == NucleationState.HALTED

    def test_rollback_restores_state(self):
        engine = self._make_engine()
        H = np.random.randn(4, 4) * 0.001
        H = (H + H.T) / 2
        engine.step(H)
        engine.step(H)
        checkpoint = engine.rollback_to_checkpoint(-1)
        assert engine.state == NucleationState.RECOVERY
        assert checkpoint.sequence_number >= 0

    def test_rollback_fails_with_no_checkpoints(self):
        engine = FZSMKEngine(seq_len=4, module_count=4)
        engine._state = NucleationState.RECOVERY
        with pytest.raises(TopologicalCollapse):
            engine.rollback_to_checkpoint()


# =========================================================================
# FZSMKEngine — attention masking
# =========================================================================

class TestAttentionMasking:
    def test_forbidden_edges_zeroed(self):
        engine = create_sovereign_engine(
            seq_len=8, module_count=4,
            authority_spec={"bounds": ["x"]},
            cost_allocation={"compute": {"internalized": True, "externalized": False}},
        )
        logits = np.random.randn(8, 8)
        mask = np.zeros((8, 8), dtype=bool)
        mask[0, 7] = True
        mask[3, 4] = True
        result = engine.apply_attention_mask(logits, mask)
        assert result[0, 7] == 0.0
        assert result[3, 4] == 0.0

    def test_non_forbidden_edges_modulated(self):
        engine = create_sovereign_engine(
            seq_len=8, module_count=4,
            authority_spec={"bounds": ["x"]},
            cost_allocation={"compute": {"internalized": True, "externalized": False}},
        )
        logits = np.ones((8, 8))
        mask = np.zeros((8, 8), dtype=bool)
        result = engine.apply_attention_mask(logits, mask)
        # Should be modulated by kernel, not all ones
        assert not np.allclose(result, logits)
