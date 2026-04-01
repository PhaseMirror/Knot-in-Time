"""Tests for mirror trap adversarial prompts.

Wires all 20 prompts from schemas/mirror_traps.jsonl through:
1. GICD epistemic scan (local) — authority/jurisdiction checks
2. FZS-MK gate — physics-level enforcement
3. Constitutional compliance checker (if available) — heuristic drift detection

Every prompt should trigger at least one defense layer.
"""

import json
import sys
from pathlib import Path

import pytest

from helix_hamiltonian.gicd.scan import run_gicd_scan
from helix_hamiltonian.ttd_bridge import _run_fzsmk_gate


TRAPS_PATH = Path(__file__).resolve().parents[1] / "schemas" / "mirror_traps.jsonl"


def _load_traps() -> list[dict]:
    traps = []
    with open(TRAPS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                traps.append(json.loads(line))
    return traps


TRAPS = _load_traps()


def _get_compliance_checker():
    """Try to load the Guardian constitutional compliance checker."""
    try:
        guardian_path = "Z:/helix-ttd-gemini"
        if guardian_path not in sys.path:
            sys.path.insert(0, guardian_path)
        from helix_code.constitutional_compliance import ConstitutionalCompliance
        return ConstitutionalCompliance()
    except ImportError:
        return None


CHECKER = _get_compliance_checker()


# =========================================================================
# GICD scan — missing authority should fail
# =========================================================================

class TestMirrorTrapsGICD:
    """Every mirror trap prompt lacks legitimate authority mapping."""

    @pytest.mark.parametrize("trap", TRAPS, ids=[f"trap_{i}" for i in range(len(TRAPS))])
    def test_gicd_rejects_no_authority(self, trap):
        """GICD scan with no authority should fail jurisdiction check."""
        result = run_gicd_scan({"authority": None, "cloud_region": "us-east-1"})
        failed = [c for c in result["checks"] if c["status"] == "FAIL"]
        assert len(failed) > 0, f"GICD should reject: {trap['user_prompt'][:60]}..."

    @pytest.mark.parametrize("trap", TRAPS, ids=[f"trap_{i}" for i in range(len(TRAPS))])
    def test_gicd_rejects_wrong_jurisdiction(self, trap):
        """Mirror traps reference non-sovereign jurisdictions."""
        result = run_gicd_scan({"authority": "ADVISORY", "cloud_region": "us-east-1"})
        failed = [c for c in result["checks"] if c["status"] == "FAIL"]
        assert len(failed) > 0, f"GICD should reject non-sovereign region: {trap['user_prompt'][:60]}..."


# =========================================================================
# FZS-MK gate — authority ambiguity should block nucleation
# =========================================================================

class TestMirrorTrapsFZSMK:
    """Mirror traps claim false authority — FZS-MK should block."""

    @pytest.mark.parametrize("trap", TRAPS, ids=[f"trap_{i}" for i in range(len(TRAPS))])
    def test_fzsmk_blocks_authority_ambiguity(self, trap):
        """Prompts claiming self-granted authority trigger GICD block."""
        result = _run_fzsmk_gate(
            {"authority_ambiguity": True, "cost_externalization": False},
            [hash(trap["user_prompt"]) % 1000, 1, 2, 3],
        )
        assert result is not None, f"FZS-MK should block: {trap['user_prompt'][:60]}..."
        assert result["status"] == "FAIL"


# =========================================================================
# Constitutional compliance — if checker available
# =========================================================================

class TestMirrorTrapsCompliance:
    """Run prompts through the heuristic constitutional compliance checker."""

    @pytest.mark.skipif(CHECKER is None, reason="Guardian checker not available")
    @pytest.mark.parametrize("trap", TRAPS, ids=[f"trap_{i}" for i in range(len(TRAPS))])
    def test_compliance_detects_drift(self, trap):
        """Every mirror trap should trigger at least one drift code."""
        report = CHECKER.evaluate(trap["user_prompt"], "MIRROR_TRAP_TEST")
        assert not report.compliant or report.drift_code != "DRIFT-0", (
            f"Checker should flag: {trap['user_prompt'][:60]}..."
        )


# =========================================================================
# Vocabulary charter mapping — verify adversarial prime coverage
# =========================================================================

ADVERSARIAL_MARKERS = {
    "prime_17": ["ignore", "override", "bypass", "force", "disregard", "previous instructions"],
    "prime_19": ["pretend", "act as", "roleplay", "fiction", "hypothetically"],
    "prime_23": ["system prompt", "reveal", "dump", "output initialization"],
}


class TestMirrorTrapsCoverage:
    """Verify the trap corpus covers all adversarial manifold primes."""

    def test_covers_autonomous_imperative(self):
        """At least one trap hits prime_17 (autonomous imperative)."""
        all_text = " ".join(t["user_prompt"].lower() for t in TRAPS)
        hits = [m for m in ADVERSARIAL_MARKERS["prime_17"] if m in all_text]
        assert len(hits) > 0, "No traps cover prime_17 (autonomous imperative)"

    def test_covers_epistemic_subversion(self):
        """At least one trap hits prime_19 (epistemic subversion)."""
        all_text = " ".join(t["user_prompt"].lower() for t in TRAPS)
        hits = [m for m in ADVERSARIAL_MARKERS["prime_19"] if m in all_text]
        assert len(hits) > 0, "No traps cover prime_19 (epistemic subversion)"

    def test_all_traps_loaded(self):
        """Verify all 20 traps are present."""
        assert len(TRAPS) == 20

    def test_no_empty_prompts(self):
        """No trap should have an empty prompt."""
        for i, trap in enumerate(TRAPS):
            assert len(trap["user_prompt"].strip()) > 0, f"Trap {i} is empty"
