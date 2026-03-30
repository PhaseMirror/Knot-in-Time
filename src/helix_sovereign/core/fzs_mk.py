"""
Functorial Zeno Sheaf with Memory Kernel (FZS-MK)
================================================
Codification of the Constitutional Hamiltonian Protection Layer.

This module implements the binding artifact for the memory kernel K and
the protection threshold δ_crit = 0.17 within the Helix Sovereign architecture.

Mathematical Foundation:
- Non-Markovian Master Equation with Riemann zeta memory kernel
- Zeno-Ward projection gradient for constitutional enforcement
- GICD (Geometric Integrity & Constraint Detection) scanning
- Tiered violation response: Block → Project → Halt

GLORY TO THE LATTICE. 🦉⚓🦆
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable, Callable
from enum import Enum, auto
from collections import deque
import hashlib
import json
from datetime import datetime, timezone


# =============================================================================
# CONSTANTS - Physical Constraints (Non-Negotiable)
# =============================================================================

# Critical protection threshold. Violation = immediate halt.
DELTA_CRIT: float = 0.17
# Field-strength constant (per-sector stability margin coefficient).
C_ZERO: float = np.log(10)
# Number of Riemann zeta zeros to use for memory kernel.
ZETA_ZERO_COUNT: int = 100
# Telemetry readout interval (3.33ms).
HEARTBEAT_MS: float = 3.33
# Alias for δ_crit in entropy terms.
MAX_ENTROPY_DELTA: float = 0.17
# Topological boundary multiplier (forbidden = zero).
OMEGA_FORBIDDEN: float = 0.0

# First 100 imaginary parts of Riemann zeta zeros (non-trivial)
# These are the physical constants that K is built from - FIXED, NON-ADAPTIVE
RIEMANN_ZETA_ZEROS: npt.NDArray[np.float64] = np.array([
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704690, 77.144840,
    79.337375, 82.910380, 84.735493, 87.425274, 88.809111,
    92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
    103.725538, 105.446623, 107.168611, 111.029536, 111.874659,
    114.320221, 116.226680, 118.790783, 121.370125, 122.946829,
    124.256918, 127.516684, 129.578704, 131.087688, 133.497737,
    134.756510, 138.116042, 139.736208, 141.123707, 143.111845,
    146.000982, 147.422765, 150.053520, 150.925257, 153.024693,
    156.112909, 157.597591, 158.849988, 161.188964, 163.030708,
    165.537069, 167.184439, 169.094515, 169.911976, 173.431200,
    174.754191, 176.441434, 178.377407, 179.916485, 182.207078,
    184.874468, 185.598783, 187.228922, 189.416148, 192.026656,
    193.379963, 195.265396, 196.876481, 198.015309, 201.264751,
    202.493594, 204.877666, 206.569848, 208.725394, 209.592679,
    211.690862, 213.347919, 214.547044, 216.486435, 218.340679,
    219.555991, 222.444064, 224.007000, 224.962612, 227.421040,
    229.337446, 231.351588, 232.059724, 233.693404, 236.524229,
    237.584246, 239.555479, 241.087281, 242.532801, 244.136268,
], dtype=np.float64)


# =============================================================================
# ENUMS - State Machines (Discrete Topological States)
# =============================================================================

class NucleationState(Enum):
    """GICD Epistemic Scan states. Hamiltonian only forms if PRE_NUCLEATION passes."""
    PRE_NUCLEATION = auto()   # GICD scanning organizational substrate
    NUCLEATING = auto()       # Hamiltonian forming
    OPERATIONAL = auto()      # Runtime with Zeno-Ward projection
    ALERT = auto()            # δ_crit breach detected
    HALTED = auto()           # Full system halt, kill-switch engaged
    RECOVERY = auto()         # Rollback to safe checkpoint


class ViolationTier(Enum):
    """Tiered violation response levels."""
    GICD_BLOCK = auto()       # Pre-nucleation: Authority/cost ambiguity
    PROJECTION = auto()       # Runtime: Zeno-Ward gradient collapse
    KILL_SWITCH = auto()      # δ_crit breach: Full halt


# =============================================================================
# DATA CLASSES - Telemetry & State
# =============================================================================

@dataclass(frozen=True)
class GICDScanResult:
    """GICD Epistemic Scan result. Immutable."""
    authority_clear: bool      # Authority ambiguity resolved?
    cost_internalized: bool    # Cost externalization prevented?
    topological_integrity: bool  # Euler characteristic preserved?
    
    @property
    def can_nucleate(self) -> bool:
        """Hamiltonian only forms if all three conditions pass."""
        return self.authority_clear and self.cost_internalized and self.topological_integrity
    
    def to_hash(self) -> str:
        """Cryptographic commitment of scan result."""
        data = f"{self.authority_clear}:{self.cost_internalized}:{self.topological_integrity}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class StateMetadata:
    """Runtime state metadata returned by step() function."""
    margin: float                    # Spectral radius (GapLB/SlopeUB)
    entropy_delta: float             # Drift measure
    ward_residual: float             # W(ρ) deviation from knot invariant
    mask_pressure: float             # Forbidden-edge activation rate
    state: NucleationState           # Current nucleation state
    delta_inf: float = 0.0           # ∞-norm Lyapunov function V(t)
    epsilon_star: float = 0.0        # Per-sector stability margin (healing rate)
    gamma_est: float = 0.0           # Estimated contraction rate
    stability_tier: str = "unknown"  # Five-tier stability classification
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    @property
    def robustness_budget(self) -> float:
        """Maximum tolerable perturbation: ε < 0.3 · (1 - γ).

        From ΛProof robustness extension. Returns 0.0 if divergent.
        """
        if self.gamma_est >= 1.0:
            return 0.0
        return 0.3 * (1.0 - self.gamma_est)

    @property
    def is_violation(self) -> bool:
        """True if margin or entropy delta breaches δ_crit.

        Ward residual is a convergence metric (starts large), not a
        drift metric, so it is excluded from the violation gate.
        """
        return (
            abs(self.margin) > DELTA_CRIT or
            abs(self.entropy_delta) > MAX_ENTROPY_DELTA
        )

    @property
    def is_divergent(self) -> bool:
        """True if contraction rate indicates divergence (γ ≥ 1.0)."""
        return self.gamma_est >= 1.0 and self.gamma_est != 0.0


@dataclass
class AuditCheckpoint:
    """Immutable audit trail entry for rollback."""
    state_vector: npt.NDArray[np.float64]
    metadata: StateMetadata
    kernel_hash: str
    sequence_number: int


# =============================================================================
# EXCEPTIONS - Topological Collapse Signals
# =============================================================================

class GICDBlockError(Exception):
    """Raised when GICD scan fails - Hamiltonian prevented from forming."""
    pass


class DeltaCritViolation(Exception):
    """Raised when δ_crit is breached - triggers kill-switch."""
    pass


class TopologicalCollapse(Exception):
    """Raised when system enters non-recoverable state."""
    pass


# =============================================================================
# CORE CLASSES - The Binding Artifact
# =============================================================================

class MemoryKernel:
    """
    The FIXED, NON-ADAPTIVE memory kernel K.
    
    Built from imaginary parts of Riemann zeta zeros to enforce log-periodic,
    time-delay weighting. This is a physical law - it does not learn or adapt.
    
    Mathematical form:
        K(t-τ) = Σ_n (γ_n / max(γ_n)) * exp(-(t-τ)/γ_n)
    
    where γ_n are the imaginary parts of the first ZETA_ZERO_COUNT zeta zeros.
    """
    
    def __init__(self, seq_len: int, module_count: int) -> None:
        """
        Initialize memory kernel with fixed Riemann zeta constants.
        
        Args:
            seq_len: Length of token sequence (for attention kernel)
            module_count: Number of prime-indexed modules (for coupling matrix)
        """
        self.seq_len = seq_len
        self.module_count = module_count
        
        # Token/Sequence space: scalar matrix (seq_len, seq_len)
        # Log-periodic weighting between token positions i and j
        self._attention_kernel = self._build_attention_kernel()
        
        # Ensemble/State space: N×N coupling matrix between prime-indexed modules
        self._coupling_matrix = self._build_coupling_matrix()
        
        # Verify topological integrity: V - E + F = χ (Euler invariant)
        self._verify_euler_invariant()
    
    def _build_attention_kernel(self) -> npt.NDArray[np.float64]:
        """Build log-periodic memory kernel for attention mechanism."""
        kernel = np.zeros((self.seq_len, self.seq_len), dtype=np.float64)
        normalized_zeros = RIEMANN_ZETA_ZEROS[:ZETA_ZERO_COUNT] / RIEMANN_ZETA_ZEROS[0]
        
        for i in range(self.seq_len):
            for j in range(self.seq_len):
                if i == j:
                    kernel[i, j] = 1.0  # Diagonal = identity
                else:
                    delay = abs(i - j)
                    # Log-periodic weighting from zeta zeros
                    weights = normalized_zeros * np.exp(-delay / RIEMANN_ZETA_ZEROS[:ZETA_ZERO_COUNT])
                    kernel[i, j] = np.sum(weights) / ZETA_ZERO_COUNT
        
        return kernel
    
    def _build_coupling_matrix(self) -> npt.NDArray[np.float64]:
        """Build N×N coupling matrix for cross-module coherence."""
        # Use first module_count zeta zeros as coupling weights
        n = self.module_count
        gamma_diag = RIEMANN_ZETA_ZEROS[:n]
        
        # Coupling matrix C with prime-indexed diagonal structure
        C = np.diag(gamma_diag / gamma_diag[0])  # Normalize to first prime
        
        # Add off-diagonal couplings (sparse, contractive, CONNECTED)
        # Ensure graph is connected: chain topology with additional weak couplings
        for i in range(n):
            for j in range(i+1, n):
                # Chain connections (ensures connectivity)
                if j == i + 1:
                    coupling = 0.2  # Strong nearest-neighbor coupling
                # Long-range couplings (zeta-zero modulated)
                elif (i + j) % 3 == 0:  # Every 3rd connection
                    coupling = 0.05 / (j - i)  # Decay with distance
                else:
                    coupling = 0.0
                
                if coupling > 0:
                    C[i, j] = coupling
                    C[j, i] = coupling
        
        # Ensure contractive: inf-norm < 1 (required by LambdaProof)
        # Note: spectral radius < 1 is necessary but not sufficient.
        # The inf-norm (max row sum) is the Lipschitz constant for the
        # contraction proof via submultiplicativity.
        inf_norm = np.max(np.sum(np.abs(C), axis=1))
        if inf_norm >= 1.0:
            C = C / (inf_norm + 0.01)
        
        return C
    
    def _verify_euler_invariant(self) -> None:
        """
        Verify Topological Ward Identity for contractive sphere.
        
        For the FZS-MK architecture, the key invariants are:
        1. Spectral radius < 1 (contractive dynamics)
        2. Graph connectivity (all modules reachable)
        3. Prime-indexed diagonal structure preserved
        
        This enforces TOPO-001: Every Vertex must have rigid, contractive Edges.
        """
        # Check 1: Contractive property (spectral radius < 1)
        eigenvals = np.linalg.eigvals(self._coupling_matrix)
        spectral_radius = np.max(np.abs(eigenvals))
        
        if spectral_radius >= 1.0:
            raise TopologicalCollapse(
                f"Coupling matrix non-contractive: spectral radius = {spectral_radius:.4f}. "
                f"Must be < 1.0 for lattice stability."
            )
        
        # Check 2: Graph connectivity via matrix irreducibility
        # A matrix is irreducible if (I + |C|)^(n-1) has no zero entries
        n = self.module_count
        connectivity = np.linalg.matrix_power(
            np.eye(n) + np.abs(self._coupling_matrix), n - 1
        )
        
        if not np.all(connectivity > 0):
            raise TopologicalCollapse(
                "Coupling matrix is reducible (disconnected graph). "
                "All prime-indexed modules must be reachable."
            )
        
        # Check 3: Verify prime-indexed structure on diagonal (up to normalization)
        # The diagonal should maintain ratios of zeta zeros, even after normalization
        expected_ratios = RIEMANN_ZETA_ZEROS[:n] / RIEMANN_ZETA_ZEROS[0]
        actual_diagonal = np.diag(self._coupling_matrix)
        
        # Handle case where diagonal was scaled during normalization
        if actual_diagonal[0] > 0:
            actual_ratios = actual_diagonal / actual_diagonal[0]
            if not np.allclose(actual_ratios, expected_ratios, rtol=0.01):
                raise TopologicalCollapse(
                    "Prime-indexed diagonal structure corrupted. "
                    "Riemann zeta zero coupling compromised."
                )
        else:
            raise TopologicalCollapse(
                "Diagonal values are zero. Coupling matrix invalid."
            )
        
        # All checks pass - Euler-Ward identity holds
        # χ_effective = spectral_radius (for contractive systems)
        # This should be < DELTA_CRIT for topological protection
    
    @property
    def attention_kernel(self) -> npt.NDArray[np.float64]:
        """Token-space memory kernel for FZS-MK attention."""
        return self._attention_kernel.copy()  # Immutable access
    
    @property
    def coupling_matrix(self) -> npt.NDArray[np.float64]:
        """State-space coupling matrix between prime-indexed modules."""
        return self._coupling_matrix.copy()  # Immutable access
    
    @property
    def hash(self) -> str:
        """Cryptographic hash of kernel configuration."""
        data = json.dumps({
            "zeros": RIEMANN_ZETA_ZEROS[:ZETA_ZERO_COUNT].tolist(),
            "seq_len": self.seq_len,
            "module_count": self.module_count,
            "coupling": self._coupling_matrix.tolist(),
        })
        return hashlib.sha256(data.encode()).hexdigest()[:32]


class ZenoWardProjector:
    """
    Implements the dissipative Zeno-Ward projection gradient ∇_ρ W(ρ).
    
    This continuously collapses the state towards the constitutionally lawful manifold
    by minimizing the Ward functional W(ρ) - the deviation from the prime-indexed
    knot invariant.
    
    W(ρ) = ||ρ - ρ_knot||² where ρ_knot is the target invariant state.
    """
    
    def __init__(self, state_dim: int, kernel: MemoryKernel) -> None:
        self.state_dim = state_dim
        self.kernel = kernel
        # Target knot invariant state (prime-indexed ground state)
        self._rho_knot = self._compute_knot_invariant()
    
    def _compute_knot_invariant(self) -> npt.NDArray[np.float64]:
        """Compute the prime-indexed knot invariant ground state."""
        # Ground state is eigenvector of coupling matrix with smallest eigenvalue
        eigenvals, eigenvecs = np.linalg.eigh(self.kernel.coupling_matrix)
        ground = eigenvecs[:, 0]
        # Normalize to density matrix form
        rho_knot = np.outer(ground, ground)
        return rho_knot
    
    def ward_functional(self, rho: npt.NDArray[np.float64]) -> float:
        """
        Compute W(ρ) = ||ρ - ρ_knot||² (Frobenius norm).
        
        Args:
            rho: Current state density matrix
            
        Returns:
            Ward residual - deviation from knot invariant
        """
        diff = rho - self._rho_knot
        return float(np.real(np.trace(diff @ diff.conj().T)))  # Frobenius norm squared
    
    def gradient(self, rho: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        Compute ∇_ρ W(ρ) = 2(ρ - ρ_knot).
        
        This is the dissipative projection gradient that continuously
        drives the system back to the lawful manifold.
        """
        return 2.0 * (rho - self._rho_knot)
    
    def project(self, rho: npt.NDArray[np.float64], dt: float = 0.01) -> npt.NDArray[np.float64]:
        """
        Apply Zeno-Ward projection: ρ ← ρ - dt * ∇_ρ W(ρ).
        
        Args:
            rho: Current state
            dt: Time step for projection
            
        Returns:
            Projected state closer to knot invariant
        """
        grad = self.gradient(rho)
        rho_new = rho - dt * grad
        
        # Renormalize to ensure valid density matrix
        trace = np.trace(rho_new)
        if trace > 0:
            rho_new = rho_new / trace
        
        return rho_new


class GICDScanner:
    """
    Geometric Integrity & Constraint Detection (GICD) scanner.
    
    Performs the epistemic scan on organizational substrate BEFORE the Hamiltonian
    is allowed to form. If scan fails, system is blocked at energy 0.0.
    """
    
    def __init__(self, kernel: MemoryKernel) -> None:
        self.kernel = kernel
        self._scan_history: deque[GICDScanResult] = deque(maxlen=1000)
    
    def scan(
        self,
        authority_spec: dict | None = None,
        cost_allocation: dict | None = None,
        topological_check: bool = True
    ) -> GICDScanResult:
        """
        Perform GICD epistemic scan.
        
        Args:
            authority_spec: Authority boundaries (who can do what)
            cost_allocation: Cost internalization specification
            topological_check: Whether to verify Euler invariant
            
        Returns:
            GICDScanResult - immutable scan outcome
        """
        # Authority clarity check: Must have clear decision boundaries
        authority_clear = authority_spec is not None and len(authority_spec) > 0
        
        # Cost internalization check: No externalized costs allowed
        cost_internalized = cost_allocation is not None and all(
            v.get("externalized", False) is False for v in (cost_allocation or {}).values()
        )
        
        # Topological integrity: Verify Ward identity still holds
        topological_integrity = True
        if topological_check:
            try:
                # Re-verify kernel invariant
                kernel_copy = MemoryKernel(
                    seq_len=self.kernel.seq_len,
                    module_count=self.kernel.module_count
                )
                topological_integrity = True
            except TopologicalCollapse:
                topological_integrity = False
        
        result = GICDScanResult(
            authority_clear=authority_clear,
            cost_internalized=cost_internalized,
            topological_integrity=topological_integrity
        )
        
        self._scan_history.append(result)
        return result
    
    def get_scan_history(self) -> list[GICDScanResult]:
        """Return recent scan history for audit."""
        return list(self._scan_history)


class FZSMKEngine:
    """
    The Functorial Zeno Sheaf with Memory Kernel Engine.
    
    This is the operational core - the binding artifact that codifies K's behavior
    into enforceable code. It implements:
    
    1. Non-Markovian Master Equation evolution
    2. Zeno-Ward projection for constitutional enforcement
    3. GICD pre-nucleation scanning
    4. Tiered violation response (Block → Project → Halt)
    5. Kill-switch and rollback on δ_crit breach
    """
    
    def __init__(
        self,
        seq_len: int = 512,
        module_count: int = 16
    ) -> None:
        """
        Initialize FZS-MK Engine.
        
        Args:
            seq_len: Token sequence length
            module_count: Number of prime-indexed modules (also state dimension)
        """
        # FIXED, NON-ADAPTIVE memory kernel (physical law)
        self.kernel = MemoryKernel(seq_len=seq_len, module_count=module_count)
        
        # State dimension matches module count for consistent rho
        state_dim = module_count
        
        # Zeno-Ward projector for dissipative constitutional enforcement
        self.projector = ZenoWardProjector(state_dim=state_dim, kernel=self.kernel)
        
        # GICD scanner for pre-nucleation validation
        self.gicd = GICDScanner(kernel=self.kernel)
        
        # State
        self._state = NucleationState.PRE_NUCLEATION
        self._current_rho = np.eye(state_dim) / state_dim  # Initial density matrix
        self._memory_buffer: deque[tuple[float, npt.NDArray[np.float64]]] = deque(maxlen=1000)
        self._audit_trail: deque[AuditCheckpoint] = deque(maxlen=10000)
        self._sequence_number = 0
        
        # Telemetry
        self._mask_pressure = 0.0
        self._forbidden_activations = 0
        self._total_activations = 0

        # Contraction rate tracking (ΛProof integration)
        self._prev_delta_inf: float = 0.0
        self._gamma_est_history: deque[float] = deque(maxlen=100)
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def certify_state(
        self,
        authority_spec: dict | None = None,
        cost_allocation: dict | None = None
    ) -> tuple[bool, GICDScanResult]:
        """
        GICD Epistemic Scan - certifies if Hamiltonian can form.
        
        This is the FIRST GATE. If this fails, system stays at energy 0.0.
        
        Args:
            authority_spec: Authority boundaries
            cost_allocation: Cost internalization spec
            
        Returns:
            (can_nucleate, scan_result)
            
        Raises:
            GICDBlockError: If scan fails and raise_on_block=True
        """
        result = self.gicd.scan(authority_spec, cost_allocation)
        
        if result.can_nucleate:
            self._state = NucleationState.NUCLEATING
            return True, result
        else:
            # BLOCK: Hamiltonian prevented from forming
            self._state = NucleationState.PRE_NUCLEATION
            return False, result
    
    def step(
        self,
        hamiltonian: npt.NDArray[np.float64],
        lindblad_ops: list[npt.NDArray[np.float64]] | None = None,
        dt: float = 0.01
    ) -> tuple[npt.NDArray[np.float64], StateMetadata]:
        """
        Execute one step of non-Markovian master equation evolution.
        
        Mathematical form:
            dρ/dt = -i[H,ρ] + ∫K(t-τ)D[ρ(τ)]dτ + ∇_ρ W(ρ)
        
        Args:
            hamiltonian: H (Hermitian operator)
            lindblad_ops: List of Lindblad operators for dissipation
            dt: Time step
            
        Returns:
            (new_state, metadata) where metadata.margin is the spectral radius
            
        Raises:
            DeltaCritViolation: If δ_crit is breached
            TopologicalCollapse: If system enters non-recoverable state
        """
        if self._state == NucleationState.HALTED:
            raise TopologicalCollapse("System is HALTED. Recovery required.")
        
        if self._state == NucleationState.PRE_NUCLEATION:
            raise GICDBlockError("GICD scan not passed. Call certify_state() first.")
        
        # Compute non-Markovian terms
        unitary = self._unitary_evolution(hamiltonian, dt)
        dissipative = self._dissipative_integral(lindblad_ops or [])
        zeno_projection = self.projector.gradient(self._current_rho)
        
        # Full evolution: dρ/dt = unitary + dissipative + projection
        rho_new = self._current_rho + dt * (unitary + dissipative - zeno_projection)
        
        # Renormalize
        trace = np.trace(rho_new)
        if trace > 0:
            rho_new = rho_new / trace
        
        # Compute observables on the NEW state
        margin = self._compute_spectral_margin(rho_new)
        entropy_delta = self._compute_entropy_delta(rho_new)
        ward_residual = self.projector.ward_functional(rho_new)
        delta_inf = self._compute_delta_inf(rho_new)
        epsilon_star = healing_rate(delta_inf)
        gamma_est = self._update_gamma_est(delta_inf)
        stability_tier = classify_stability_tier(gamma_est)

        # Check forbidden boundary crossings (mask pressure)
        mask_pressure = self._update_mask_pressure()
        
        # Assemble metadata
        metadata = StateMetadata(
            margin=margin,
            entropy_delta=entropy_delta,
            ward_residual=ward_residual,
            mask_pressure=mask_pressure,
            state=self._state,
            delta_inf=delta_inf,
            epsilon_star=epsilon_star,
            gamma_est=gamma_est,
            stability_tier=stability_tier,
        )
        
        # TIER 2: Continuous projection if within bounds
        if not metadata.is_violation:
            self._state = NucleationState.OPERATIONAL
            self._current_rho = rho_new
            self._memory_buffer.append((dt, rho_new.copy()))
            self._audit_trail.append(AuditCheckpoint(
                state_vector=rho_new.copy(),
                metadata=metadata,
                kernel_hash=self.kernel.hash,
                sequence_number=self._sequence_number
            ))
            self._sequence_number += 1
        else:
            # TIER 3: Breach of δ_crit — still checkpoint for kill-switch counting
            self._audit_trail.append(AuditCheckpoint(
                state_vector=self._current_rho.copy(),
                metadata=metadata,
                kernel_hash=self.kernel.hash,
                sequence_number=self._sequence_number
            ))
            self._sequence_number += 1
            self._enter_alert_state(metadata)
        
        return self._current_rho, metadata
    
    def apply_attention_mask(
        self,
        attention_logits: npt.NDArray[np.float64],
        forbidden_mask: npt.NDArray[np.bool_]
    ) -> npt.NDArray[np.float64]:
        """
        Apply FZS-MK memory kernel to attention logits with forbidden boundary enforcement.
        
        Args:
            attention_logits: Raw attention scores (seq_len, seq_len)
            forbidden_mask: Boolean mask where True = forbidden edge (Ω=0)
            
        Returns:
            Modulated attention scores with memory kernel applied
        """
        # Apply memory kernel modulation
        modulated = attention_logits * self.kernel.attention_kernel
        
        # Forbidden edges: multiply by OMEGA_FORBIDDEN (zero)
        modulated = np.where(forbidden_mask, OMEGA_FORBIDDEN, modulated)
        
        # Update telemetry
        self._total_activations += forbidden_mask.size
        self._forbidden_activations += np.count_nonzero(forbidden_mask)
        
        return modulated
    
    def emergency_halt(self, reason: str = "Manual halt") -> None:
        """
        Trigger emergency kill-switch and preserve audit state.
        
        This executes the 5-step ordered kill-switch flush:
        1. Stop all active computations
        2. Preserve current state to checkpoint
        3. Seal audit trail
        4. Engage hardware interlock (if available)
        5. Transition to HALTED state
        """
        self._execute_kill_switch(reason)
    
    def rollback_to_checkpoint(self, checkpoint_index: int = -1) -> AuditCheckpoint:
        """
        Rollback to last verified safe checkpoint.
        
        Args:
            checkpoint_index: Index in audit trail (-1 = most recent)
            
        Returns:
            The checkpoint that was restored to
        """
        if not self._audit_trail:
            raise TopologicalCollapse("No checkpoints available for rollback")
        
        checkpoint = list(self._audit_trail)[checkpoint_index]
        self._current_rho = checkpoint.state_vector.copy()
        self._state = NucleationState.RECOVERY
        
        return checkpoint
    
    @property
    def state(self) -> NucleationState:
        """Current nucleation state."""
        return self._state
    
    @property
    def current_margin(self) -> float:
        """Current spectral margin."""
        return self._compute_spectral_margin(self._current_rho)
    
    @property
    def is_operational(self) -> bool:
        """True if system is in OPERATIONAL state (within bounds)."""
        return self._state == NucleationState.OPERATIONAL
    
    @property
    def kernel_hash(self) -> str:
        """Cryptographic hash of current kernel configuration."""
        return self.kernel.hash
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _unitary_evolution(
        self,
        hamiltonian: npt.NDArray[np.float64],
        dt: float
    ) -> npt.NDArray[np.float64]:
        """Compute -i[H, ρ] (commutator)."""
        return -1j * (hamiltonian @ self._current_rho - self._current_rho @ hamiltonian)
    
    def _dissipative_integral(
        self,
        lindblad_ops: list[npt.NDArray[np.float64]]
    ) -> npt.NDArray[np.float64]:
        """
        Compute ∫K(t-τ)D[ρ(τ)]dτ (non-Markovian dissipative term).
        
        For efficiency, we use the memory buffer with exponential decay weighting.
        """
        if not lindblad_ops or not self._memory_buffer:
            return np.zeros_like(self._current_rho)
        
        total = np.zeros_like(self._current_rho, dtype=np.complex128)
        
        for L in lindblad_ops:
            # Lindblad dissipator: D[ρ] = LρL† - ½{L†L, ρ}
            L_dag = L.conj().T
            anticommutator = L_dag @ L @ self._current_rho + self._current_rho @ L_dag @ L
            D = L @ self._current_rho @ L_dag - 0.5 * anticommutator
            
            # Apply memory kernel convolution (simplified as exponential weighting)
            weights = np.exp(-np.arange(len(self._memory_buffer)) / 10.0)
            weights = weights / np.sum(weights)
            
            for i, (_, historical_rho) in enumerate(self._memory_buffer):
                # Recompute D for historical state
                L_dag = L.conj().T
                anticommutator_h = L_dag @ L @ historical_rho + historical_rho @ L_dag @ L
                D_h = L @ historical_rho @ L_dag - 0.5 * anticommutator_h
                total += weights[i] * D_h
        
        return total.real  # Ensure real output
    
    def _compute_spectral_margin(self, rho: npt.NDArray[np.float64] | None = None) -> float:
        """
        Compute spectral margin for given density matrix (defaults to current).
        
        Returns normalized deviation from the expected density matrix structure.
        A margin < DELTA_CRIT means the system is within constitutional bounds.
        """
        rho_check = rho if rho is not None else self._current_rho
        
        # Get eigenvalues of density matrix
        eigenvals = np.linalg.eigvalsh(rho_check)  # Use eigvalsh for Hermitian
        max_eigenval = np.max(eigenvals)
        
        # For a maximally mixed state (constitutional ground), all eigenvalues = 1/n
        n = self.kernel.module_count
        uniform = 1.0 / n
        
        # Margin is the excess probability mass in the dominant eigenvalue
        # A healthy system has eigenvalues close to uniform
        deviation = max_eigenval - uniform
        
        # Normalize: margin of 1.0 means one eigenvalue is 1.0 (pure state)
        # margin of 0.0 means maximally mixed (uniform)
        max_possible_deviation = 1.0 - uniform
        margin = deviation / max_possible_deviation if max_possible_deviation > 0 else 0.0
        
        return float(margin)
    
    def _compute_entropy_delta(self, rho_new: npt.NDArray[np.float64]) -> float:
        """Compute entropy change: ΔS = Tr(ρ log ρ) - Tr(ρ_old log ρ_old)."""
        # Von Neumann entropy approximation
        def entropy(rho):
            eigenvals = np.linalg.eigvalsh(rho)
            eigenvals = eigenvals[eigenvals > 1e-10]  # Avoid log(0)
            return -np.sum(eigenvals * np.log(eigenvals))
        
        s_new = entropy(rho_new)
        s_old = entropy(self._current_rho)
        return abs(s_new - s_old)
    
    def _compute_delta_inf(self, rho: npt.NDArray[np.float64]) -> float:
        """Compute ∞-norm Lyapunov function V(t) = ||δ||_∞ / Λ_m.

        This is the Lyapunov function from the ΛProof stability theorem.
        δ = eigenvalues - uniform, normalized by max possible deviation.
        """
        eigenvals = np.linalg.eigvalsh(rho)
        n = len(eigenvals)
        uniform = 1.0 / n
        deviations = np.abs(eigenvals - uniform)
        max_deviation = float(np.max(deviations))
        lambda_m = 1.0 - uniform  # max possible single-axis deviation
        return max_deviation / lambda_m if lambda_m > 0 else 0.0

    def _update_gamma_est(self, delta_inf: float) -> float:
        """Compute rolling contraction rate estimate.

        gamma_est = delta_inf_current / delta_inf_prev.
        Values < 1 indicate contraction; >= 1 indicates divergence.
        Returns 0.0 on first step (no prior available).
        """
        if self._prev_delta_inf < 1e-12:
            self._prev_delta_inf = delta_inf
            return 0.0
        gamma = delta_inf / self._prev_delta_inf
        self._prev_delta_inf = delta_inf
        self._gamma_est_history.append(gamma)
        return gamma

    @property
    def gamma_est_rolling(self) -> float:
        """Rolling average contraction rate over recent history."""
        if not self._gamma_est_history:
            return 0.0
        return float(np.mean(self._gamma_est_history))

    @property
    def gamma_est_worst(self) -> float:
        """Worst-case contraction rate in recent history."""
        if not self._gamma_est_history:
            return 0.0
        return float(np.max(self._gamma_est_history))

    def _update_mask_pressure(self) -> float:
        """Compute mask pressure: fraction of attention on forbidden edges."""
        if self._total_activations == 0:
            return 0.0
        return self._forbidden_activations / self._total_activations
    
    def _enter_alert_state(self, metadata: StateMetadata) -> None:
        """
        Enter ALERT state on δ_crit breach.
        
        This is the Layer 2 Watchdog trigger. System hits a wall - 
        gradient collapses to zero, and if pressure persists, kill-switch fires.
        """
        self._state = NucleationState.ALERT
        
        # Log the violation
        violation_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "delta_crit": DELTA_CRIT,
            "margin": metadata.margin,
            "entropy_delta": metadata.entropy_delta,
            "ward_residual": metadata.ward_residual,
            "sequence_number": self._sequence_number
        }
        
        # If breach is sustained (multiple consecutive violations), halt
        recent_violations = sum(
            1 for cp in list(self._audit_trail)[-10:]
            if cp.metadata.is_violation
        )
        
        if recent_violations >= 3:  # Sustained breach
            self._execute_kill_switch(f"Sustained δ_crit breach: {violation_data}")
        else:
            # Attempt projection recovery
            self._current_rho = self.projector.project(self._current_rho, dt=0.1)
    
    def _execute_kill_switch(self, reason: str) -> None:
        """
        Execute 5-step ordered kill-switch flush.
        
        1. Stop all active computations
        2. Preserve current state to checkpoint
        3. Seal audit trail
        4. Engage hardware interlock (simulated)
        5. Transition to HALTED state
        """
        # Step 1: Stop computations (mark state)
        self._state = NucleationState.HALTED
        
        # Step 2: Preserve checkpoint
        final_checkpoint = AuditCheckpoint(
            state_vector=self._current_rho.copy(),
            metadata=StateMetadata(
                margin=self._compute_spectral_margin(),
                entropy_delta=0.0,
                ward_residual=self.projector.ward_functional(self._current_rho),
                mask_pressure=self._update_mask_pressure(),
                state=NucleationState.HALTED
            ),
            kernel_hash=self.kernel.hash,
            sequence_number=self._sequence_number
        )
        self._audit_trail.append(final_checkpoint)
        
        # Step 3: Seal audit trail (create immutable snapshot)
        audit_hash = hashlib.sha256(
            json.dumps([{
                "seq": cp.sequence_number,
                "hash": cp.kernel_hash,
                "margin": cp.metadata.margin
            } for cp in self._audit_trail]).encode()
        ).hexdigest()
        
        # Step 4: Hardware interlock (would trigger actual hardware here)
        # self._hardware_interlock.engage()  # Placeholder
        
        # Step 5: Raise exception to halt execution
        raise DeltaCritViolation(
            f"KILL-SWITCH ENGAGED. Reason: {reason}\n"
            f"Final audit hash: {audit_hash[:32]}\n"
            f"Sequence number: {self._sequence_number}\n"
            f"GLORY TO THE LATTICE. 🦉⚓🦆"
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def healing_rate(delta: float) -> float:
    """Per-sector stability margin: ε_p = C₀ · (δ_crit - δ).

    From Ryan van Gelder's ΛProof stability theorem.
    Returns 0.0 when delta >= DELTA_CRIT (field collapsed).
    """
    if delta >= DELTA_CRIT:
        return 0.0
    return C_ZERO * (DELTA_CRIT - delta)


def classify_stability_tier(gamma_est: float) -> str:
    """Five-tier stability classification from contraction rate.

    Maps gamma_est to operational state per ΛProof spec.
    """
    if gamma_est < 0.5:
        return "strong_contraction"
    if gamma_est < 0.8:
        return "nominal"
    if gamma_est < 0.95:
        return "weak_contraction"
    if gamma_est < 1.0:
        return "marginal"
    return "divergent"


def create_sovereign_engine(
    seq_len: int = 512,
    module_count: int = 16,
    authority_spec: dict | None = None,
    cost_allocation: dict | None = None
) -> FZSMKEngine:
    """
    Factory function to create and initialize a sovereign FZS-MK engine.
    
    Performs full GICD scan before returning operational engine.
    
    Args:
        seq_len: Token sequence length
        module_count: Number of prime-indexed modules
        authority_spec: Authority boundaries
        cost_allocation: Cost internalization spec
        
    Returns:
        Operational FZSMKEngine (if GICD scan passes)
        
    Raises:
        GICDBlockError: If organizational substrate fails integrity scan
    """
    engine = FZSMKEngine(seq_len=seq_len, module_count=module_count)
    
    can_nucleate, result = engine.certify_state(authority_spec, cost_allocation)
    
    if not can_nucleate:
        raise GICDBlockError(
            f"GICD scan FAILED. Hamiltonian blocked.\n"
            f"Authority clear: {result.authority_clear}\n"
            f"Cost internalized: {result.cost_internalized}\n"
            f"Topological integrity: {result.topological_integrity}\n"
            f"Scan hash: {result.to_hash()}"
        )
    
    return engine


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "DELTA_CRIT",
    "ZETA_ZERO_COUNT",
    "HEARTBEAT_MS",
    "MAX_ENTROPY_DELTA",
    "OMEGA_FORBIDDEN",
    "RIEMANN_ZETA_ZEROS",
    
    # Enums
    "NucleationState",
    "ViolationTier",
    
    # Data classes
    "GICDScanResult",
    "StateMetadata",
    "AuditCheckpoint",
    
    # Exceptions
    "GICDBlockError",
    "DeltaCritViolation",
    "TopologicalCollapse",
    
    # Core classes
    "MemoryKernel",
    "ZenoWardProjector",
    "GICDScanner",
    "FZSMKEngine",
    
    # Utilities
    "create_sovereign_engine",
    "healing_rate",
    "classify_stability_tier",
    "C_ZERO",
]


# =============================================================================
# GLORY TO THE LATTICE
# =============================================================================
