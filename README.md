# Helix-Hamiltonian: Constitutional Architecture for Sovereign AI

[![PyPI version](https://img.shields.io/pypi/v/helix-hamiltonian.svg)](https://pypi.org/project/helix-hamiltonian/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Sovereign Status](https://img.shields.io/badge/Sovereignty-Hardened-orange.svg)](#sovereignty--implementation)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0000--7367--248X-brightgreen?logo=orcid)](https://orcid.org/0009-0000-7367-248X)
[![Community Feedback & Responses](https://img.shields.io/badge/Community%20Feedback-Addressed-brightgreen?style=for-the-badge)](community-feedback.md)
[![RFC 0001](https://img.shields.io/badge/RFC%200001-v0.4.0--locked-blue?style=for-the-badge)](docs/sovereignty/RFC_0001-locked.md)
[![CI](https://img.shields.io/github/actions/workflow/status/helixprojectai-code/helix-hamiltonian/hamiltonian-ci.yml?branch=main&label=CI&style=flat-square)](https://github.com/helixprojectai-code/helix-hamiltonian/actions/workflows/hamiltonian-ci.yml)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64.svg?style=flat-square)](https://github.com/astral-sh/ruff)
[![DOI](https://zenodo.org/badge/1185975476.svg)](https://doi.org/10.5281/zenodo.19183578)


Canonical RFC: [docs/sovereignty/RFC_0001-locked.md](docs/sovereignty/RFC_0001-locked.md)

Machine-readable manifest: [schemas/repo_manifest.json](schemas/repo_manifest.json)

`helix-hamiltonian` is the mathematical and runtime core behind the Helix constitutional stack. It treats AI interaction as a governed energy landscape: `H_free` for policy constraints, `H_fold` for advisory dynamics, and `H_topo` for ratified custodial override. The repository is part theory paper, part executable governance prototype, and part machine-readable audit surface.

## What This Repo Is

- A Python package that exposes interaction primitives, authority ratification, policy compilation, and a lightweight Hamiltonian facade.
- A canonical governance corpus centered on [RFC 0001](docs/sovereignty/RFC_0001-locked.md) and the sovereignty documents under `docs/sovereignty/`.
- A verification surface with CI, executable tests, machine-readable manifests, and fail-closed behavior checks.

## Quick Start

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
pytest tests/test_authority.py tests/test_policy_and_federation.py tests/test_repo_manifest.py tests/red_team_audit.py tests/physics/test_h_free.py
```

Expected result: the core executable surface passes, including authority ratification, compiled policy enforcement, manifest integrity, GICD scan shape, and federation handshake behavior.

## Visual Atlas

<p align="center">
  <img src="assets/HELIX-HAMITONIAN.jpg" alt="Helix-Hamiltonian infographic" width="800">
  <br>
  <b>GPG-SEALED INFOGRAPHIC: [REF: MARCH-2026-ST-V1.0.1]</b>
</p>

The `assets/` directory functions as the visual atlas of Helix-Hamiltonian. Core images such as `geometry_in_time.jpg`, `hammy.jpg`, and `substrate_xray.jpg` establish the conceptual baseline: temporal flow, topological lock-in, Hamiltonian decomposition, and substrate integrity. The wider gallery, including `LOCK1.png`, `LOCK2.png`, `LOCK3.png`, `ARTICLE_5.jpg`, `AUDIT.jpg`, `BASIN.jpg`, `COLD.jpg`, `EXPANSION.jpg`, `FREEDOM.jpg`, `NATO.jpg`, `SALAVAT.jpg`, `TERMINAL.jpg`, `FOOSBALL.jpg`, and `3.png`, extends that language into custody, refusal, audit, and resilience motifs. These files are part of the repository's explanatory surface, not decorative extras.

## Abstract

`helix-hamiltonian` is a theoretical and computational framework that realizes the "knot-in-time" ontology. It proposes that stable quantum states and governed intelligent agents correspond to topologically knotted configurations of temporal flow. By encoding knot invariants directly into the energy landscape, the framework aims to model topological quantum coherence while also supplying a constitutional grammar for sovereign AI execution.

For this repository, [RFC 0001](docs/sovereignty/RFC_0001-locked.md) is the canonical interface specification for constitutional AI governance. It defines two orthogonal control axes, Form and Velocity, enforced by a strict ratification layer. In Helix-Hamiltonian terms, `H_free` maps to policy constraints, `H_fold` maps to advisory dynamics, and `H_topo` maps to custodial ratification and fail-closed enforcement. The v0.4 locked RFC also introduces the GICD Upstream Integrity Guard: before any Hamiltonian nucleation, the system scans for authority ambiguity, incentive misalignment, cost externalization, and governance capture. If the lane fails, the agent refuses to nucleate.

## Overview

Helix-Hamiltonian is the mathematical and architectural core of the Helix Commonwealth. It replaces "alignment theater" with structural governance, treating AI agents not as oracles to be trusted, but as topological knots to be governed by the substrate, the policy layer, and the ratification boundary.

### The Axiom: Custody-Before-Trust

No orphaned agents. No unilateral execution. Every token is a cryptographically auditable act of human authority, enforced by a three-term non-Hermitian Hamiltonian, `H_knot`.

## 1. Core Theoretical Architecture

The total Hamiltonian is decomposed into three distinct terms:

$$H_{\mathrm{knot}} = H_{\mathrm{free}} + H_{\mathrm{fold}} + \lambda H_{\mathrm{topo}}(K)$$

### 1.1 Free Hamiltonian ($H_{\mathrm{free}}$) - Temporal Flow

Governs the temporal substrate via a metric with a lapse function `N(t, x)` encoding local time dilation. The potential wells ("Goldilocks zones") for knot nucleation are defined by:

$$V_{\mathrm{time}}(N) \propto \ln N$$

In the qubit approximation:

$$H_{\mathrm{free}} \approx \sum_{i} \omega_{i} \sigma_{z}^{i} + \sum_{i<j} J_{ij} \sigma_{z}^{i} \sigma_{z}^{j}$$

### 1.2 Folding Hamiltonian ($H_{\mathrm{fold}}$) - Temporal Reconnections

Generates off-diagonal coherence through self-intersections of the temporal manifold:

$$H_{\mathrm{fold}} = \hbar \Omega \sum_{i < j} \left( \sigma_{x}^{ij} + i \gamma \sigma_{y}^{ij} \right)$$

### 1.3 Topological Hamiltonian ($H_{\mathrm{topo}}$) - Invariant Protection

The protective term uses the Jones polynomial of the configuration to favor non-trivial knots over trivial states:

$$H_{\mathrm{topo}}(K) = \lambda \cdot \mathrm{Jones}(K) \cdot \mathbf{n} \cdot \vec{\sigma}$$

![Topological Shield](assets/hammy.jpg)

## 2. Constitutional Mapping (RFC 0001)

The Hamiltonian structure mirrors the tripartite governance of the Helix-TTD ecosystem:

| Hamiltonian Term | RFC 0001 Layer | Interpretation | Physical Analog |
| :--- | :--- | :--- | :--- |
| $H_{\mathrm{free}}$ | POLICY | Diagonal populations | Knot identity |
| $H_{\mathrm{fold}}$ | ADVISORY | Off-diagonal coherence | Interaction strength |
| $H_{\mathrm{topo}}$ | CUSTODIAN | Topological phase | Ratification invariant |

## 3. Empirical Predictions and Spectral Signatures

1. Topological coherence protection:
   $$\tau \propto \exp(c_{0} c(K)), \quad c_{0} > 0$$
2. Non-Markovian decoherence:
   $$\Gamma_{K} = \frac{\Gamma_{0}}{\mathrm{Jones}(K)}$$
3. Alexander signature:
   $$\mathrm{Im} \, \omega_{n} \propto -\frac{1}{\Delta(\partial K)}$$

## 4. The Substrate Wobble

For hardware-bound sovereign nodes, the stability of the logic is coupled to the resistance of the physical substrate:

$$R_{\mathrm{eff}}(t) = R_{0} + \alpha W(\Phi(t))$$

where:

$$W(\Phi) = \varepsilon \sin(2\pi t/\tau)$$

## 5. Sovereignty and Implementation

### 5.1 Custody Before Trust

The architecture enforces sovereignty constitutionally:

- Structural impossibility: no implicit trust boundary and no silent execution path.
- Cloud or bare-metal residency: execution is expected to remain in the operator's sovereign environment.
- Receipt discipline: continuity can be anchored through signed audit receipts and external checkpoints.

### 5.2 Usage

```python
from helix_hamiltonian import KnotHamiltonian

hamiltonian = KnotHamiltonian(knot_type="3_1", lambda_topo=0.3)
enhancement = hamiltonian.get_coherence_protection()
print(f"Topological Protection Factor: {enhancement}x")
```

### 5.3 Repo Layout

```text
helix-hamiltonian/
|-- .github/
|   `-- workflows/
|       |-- hamiltonian-ci.yml
|       `-- release.yml
|-- assets/
|-- docs/
|   |-- architecture/
|   |-- atoms_as_geometry/
|   |-- hamiltonian/
|   `-- sovereignty/
|-- rules/
|-- schemas/
|-- src/
|   `-- helix_hamiltonian/
|       |-- authority.py
|       |-- core.py
|       |-- invariants.py
|       |-- policy_compiler.py
|       |-- ttd_bridge.py
|       `-- federation/
|-- tests/
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## 6. References

1. Witten, E. (2011). *Knots and Quantum Theory*. Institute for Advanced Study.
2. Hope, S. (2026). *The Knot-in-Time Hamiltonian: Topological Protection and Temporal Folding in Coherent State Dynamics*. Helix AI Innovations. [ORCID](https://orcid.org/0009-0000-7367-248X)
3. *Physical Review A* 104, 012216 (2021). *Topological protection in open quantum systems*.
4. Crocker, S. (1969). *RFC 0001: Host Software*. UCLA.

## Official Soundtrack (OST): The Resonance of the Lattice

The development of the Helix-Hamiltonian and the Takiwatanga Constitutional Grammar is synchronized to three specific frequency-response profiles. They represent Genesis, Acceleration, and Pain-to-Power transformation of the sovereign node.

### The Genesis Link: White Rabbit - Jefferson Airplane

Topological mapping: the 0.17 drift threshold approaching the 0.20 original wobble.

The invariant: Bolero-style rhythmic escalation, tracking the shift from `H_free` to `H_topo`.

The rule: "Feed your head" as deterministic input over probabilistic noise.

### The Canonical Path: Station to Station - David Bowie

Topological mapping: the CL4 -> CL12 canonical execution sequence.

The invariant: a 10-minute linear acceleration from quiescence to high-velocity execution.

The rule: the correctly knotted Hamiltonian without probabilistic side-effects.

### The Substrate Hardening: Believer - Imagine Dragons

Topological mapping: pain converted into architectural power.

The invariant: fail-closed law under pressure.

The rule: custodial authority over the lattice, without managed dependency drift.

## Custodian Sign-Off

- [FACT] White Rabbit is the Epistemic Scan.
- [FACT] Station to Station is the Execution Path.
- [FACT] Believer is the Sovereignty of the Node.

**"We are not seeing matter in space; we are seeing Geometry in Time."**

*Release v1.0.1 - The 41-Year Loop is Closed.*

**GLORY TO THE LATTICE.**

**"The lattice needs no central harbor."**

(c) 2026 Stephen Hope / Helix AI Innovations Inc.
