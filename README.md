# Primacía Informacional Topológica (PIT)

**Topological Informational Primacy: Topology is Fundamental, Metric is Emergent**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18408176.svg)](https://doi.org/10.5281/zenodo.18408176)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Axiom

> **In every physical system, topological changes PRECEDE and CAUSE metric/dynamical changes.**

```
t_topology < t_metric
```

In the thermodynamic limit, this is deterministic, not stochastic.

## Ontological Claim

Reality has TWO layers:

1. **TOPOLOGICAL LAYER** (fundamental)
   - Homology, Betti numbers
   - Persistence diagrams
   - Topological entropy

2. **METRIC LAYER** (emergent)
   - Distances, angles
   - Curvature, geodesics
   - Physical observables

Classical and quantum physics operate on the metric layer.
PIT claims the topological layer GENERATES it.

## Mathematical Framework

### Topological State Space (TSS)

For any physical system X with configuration q, define:

```
TSS(X) = { PD_k(X, ε) : k ∈ ℕ, ε ∈ ℝ⁺ }
```

where PD_k is the k-dimensional persistence diagram at filtration scale ε.

### Topological Entropy

Given persistence diagram D = {(bᵢ, dᵢ)}, the persistent entropy is:

```
S_T = -Σᵢ pᵢ log(pᵢ)
```

where pᵢ = lᵢ/L is the normalized lifetime (lᵢ = dᵢ - bᵢ).

### Primacy Theorem

**Theorem:** For a system undergoing phase transition in thermodynamic limit:

```
lim_{N→∞} P(t_T < t_M | transition) = 1
```

where:
- t_T = time of topological change (detected via CUSUM on S_T)
- t_M = time of metric change (traditional order parameter)

**Topology always precedes metric.**

### Dynamics in TSS

Evolution in topological state space:

```
dS_T/dt = -Γ (S_T - S_T^eq) + η(t)
```

where:
- Γ = topological relaxation rate
- S_T^eq = equilibrium entropy of target phase
- η(t) = finite-size fluctuations

## Implications

### 1. Phase Transitions

All phase transitions are fundamentally topological events:
- Crystallization: loop structure (H1) collapses
- BKT transition: vortex topology changes
- Synchronization: connectivity (H0) reorganizes

### 2. Dark Matter

If PIT is correct, dark matter is NOT a particle.
It is a manifestation of topological structure at galactic scales.

The "missing mass" is the metric's attempt to interpret topological effects.

### 3. Dark Energy

Cosmic acceleration may be an emergent metric phenomenon
from underlying topological dynamics of spacetime.

### 4. Gravity

Gravity is not fundamental—it emerges from topology.
Einstein's metric g_μν is a projection of the topological state.

## Falsifiable Predictions

1. **Universal Precedence**: In ANY phase transition, t_T < t_M
   - Test: Find a system where metric changes before topology
   - If found: PIT is FALSE

2. **Dark Matter Non-Detection**: DM will never be directly detected
   - Test: All direct detection experiments
   - If detected as particle: PIT is FALSE

3. **Scale Invariance**: The primacy principle holds at all scales
   - Molecular, stellar, galactic, cosmological
   - Test: Verify across 30+ orders of magnitude

4. **Topological Threshold**: Fundamental constants derivable from topology
   - Example: MOND's a₀ should emerge from topological analysis
   - Test: Derive a₀ from first principles

## Repository Structure

```
PIT-Topological-Primacy/
├── README.md
├── LICENSE
├── theory/
│   ├── axioms.md           # Formal axiomatization
│   ├── theorems.md         # Proofs and derivations
│   └── implications.md     # Physical consequences
├── src/
│   ├── pit_core.py         # Core TDA functions
│   ├── cusum.py            # Change detection
│   ├── entropy.py          # Topological entropy
│   └── phase_space.py      # Delay embedding
├── tests/
│   ├── test_oscillator.py  # Hopf bifurcation
│   ├── test_particles.py   # Crystallization
│   ├── test_spins.py       # BKT transition
│   └── test_cosmology.py   # Cosmic expansion
├── results/
│   └── *.json              # Experimental results
└── docs/
    ├── roadmap.md          # Research program
    └── falsification.md    # How to disprove PIT
```

## Usage

```python
from pit_core import TopologicalAnalyzer, CUSUMDetector

# Analyze any time series / point cloud
analyzer = TopologicalAnalyzer()
S_T = analyzer.persistence_entropy(data, dim=1)

# Detect topological transition
detector = CUSUMDetector(k=0.5, h=4.0)
detector.calibrate(baseline)
t_topo = detector.detect(S_T)

# Compare with metric transition
assert t_topo < t_metric, "PIT violated!"
```

## Research Program

### Phase 1: Empirical Validation
- [ ] 10+ physical systems with verified t_T < t_M
- [ ] Cross-scale validation (nm to Mpc)
- [ ] Statistical significance (p < 0.001)

### Phase 2: Theoretical Development
- [ ] Covariant formulation
- [ ] Derivation of fundamental constants
- [ ] Connection to information theory

### Phase 3: Unification
- [ ] Incorporate Standard Model
- [ ] Derive gravity from topology
- [ ] Explain quantum measurement

## Author

**Francisco Molina-Burgos**
Mérida, Yucatán, México
January 2026

---

> *"Physics is the shadow that topology casts on our instruments."*
