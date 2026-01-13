"""
PIT Core Library - Topological Informational Primacy

Core functions for computing topological observables and detecting
phase transitions via the PIT principle: t_topology < t_metric

Author: F. Molina-Burgos
Date: January 2026
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from typing import Optional, List, Tuple, Union

# Try to import ripser for exact persistence
try:
    from ripser import ripser
    HAS_RIPSER = True
except ImportError:
    HAS_RIPSER = False


class PersistenceDiagram:
    """Container for persistence diagram data"""

    def __init__(self, births: np.ndarray, deaths: np.ndarray, dim: int):
        self.births = births
        self.deaths = deaths
        self.dim = dim
        self.lifetimes = deaths - births

    def entropy(self) -> float:
        """Compute persistence entropy S_T"""
        lifetimes = self.lifetimes[np.isfinite(self.lifetimes)]
        lifetimes = lifetimes[lifetimes > 0]

        if len(lifetimes) == 0:
            return 0.0

        total = np.sum(lifetimes)
        p = lifetimes / total
        return -np.sum(p * np.log(p + 1e-10))

    def total_persistence(self) -> float:
        """Sum of all lifetimes"""
        lifetimes = self.lifetimes[np.isfinite(self.lifetimes)]
        return np.sum(lifetimes[lifetimes > 0])

    def n_features(self) -> int:
        """Number of topological features"""
        return len(self.lifetimes[np.isfinite(self.lifetimes)])


class TopologicalAnalyzer:
    """
    Main class for topological analysis of point clouds and time series.

    Implements the core PIT methodology:
    1. Compute Vietoris-Rips complex
    2. Calculate persistent homology
    3. Extract topological entropy S_T
    """

    def __init__(self, use_exact: bool = True):
        """
        Initialize analyzer.

        Args:
            use_exact: Use exact persistence (ripser) if available.
                      Falls back to Euler approximation if not.
        """
        self.use_exact = use_exact and HAS_RIPSER

    def compute_persistence(
        self,
        points: np.ndarray,
        max_dim: int = 1,
        max_edge: Optional[float] = None
    ) -> List[PersistenceDiagram]:
        """
        Compute persistent homology of a point cloud.

        Args:
            points: (N, d) array of N points in d dimensions
            max_dim: Maximum homology dimension to compute
            max_edge: Maximum edge length for Rips complex

        Returns:
            List of PersistenceDiagram objects for dimensions 0 to max_dim
        """
        if len(points) < 3:
            return [PersistenceDiagram(np.array([]), np.array([]), k)
                    for k in range(max_dim + 1)]

        # Compute distance matrix
        dm = squareform(pdist(points))

        if max_edge is None:
            max_edge = np.percentile(dm, 90)

        if self.use_exact:
            return self._ripser_persistence(dm, max_dim, max_edge)
        else:
            return self._euler_persistence(dm, max_dim, max_edge)

    def _ripser_persistence(
        self,
        dm: np.ndarray,
        max_dim: int,
        max_edge: float
    ) -> List[PersistenceDiagram]:
        """Exact persistence using ripser"""
        result = ripser(dm, maxdim=max_dim, distance_matrix=True, thresh=max_edge)

        diagrams = []
        for k, dgm in enumerate(result['dgms']):
            if len(dgm) == 0:
                diagrams.append(PersistenceDiagram(np.array([]), np.array([]), k))
            else:
                diagrams.append(PersistenceDiagram(dgm[:, 0], dgm[:, 1], k))

        return diagrams

    def _euler_persistence(
        self,
        dm: np.ndarray,
        max_dim: int,
        max_edge: float
    ) -> List[PersistenceDiagram]:
        """
        Approximate persistence using Euler characteristic.

        This is faster but loses birth/death information.
        Uses the relation: χ = β₀ - β₁ + β₂ - ...
        """
        n = len(dm)
        n_scales = 20
        scales = np.linspace(0.01 * max_edge, max_edge, n_scales)

        # Track Betti numbers at each scale
        betti_curves = {k: [] for k in range(max_dim + 1)}

        for eps in scales:
            # Count simplices
            adj = dm < eps
            np.fill_diagonal(adj, False)

            # β₀: connected components (approximate)
            n_edges = np.sum(adj) // 2
            beta_0 = max(1, n - n_edges // 2)  # Very rough

            # β₁: approximate from Euler
            # χ ≈ V - E + F, β₁ ≈ E - V + β₀ - F
            # Estimate faces (triangles)
            n_triangles = 0
            for i in range(n):
                neighbors = np.where(adj[i])[0]
                for j in neighbors:
                    if j > i:
                        common = np.sum(adj[i] & adj[j])
                        n_triangles += common

            n_triangles //= 6  # Each triangle counted 6 times

            beta_1 = max(0, n_edges - n + beta_0 - n_triangles)

            betti_curves[0].append(beta_0)
            if max_dim >= 1:
                betti_curves[1].append(beta_1)

        # Convert to pseudo-persistence diagrams
        diagrams = []

        for k in range(max_dim + 1):
            curve = np.array(betti_curves.get(k, []))
            if len(curve) == 0:
                diagrams.append(PersistenceDiagram(np.array([]), np.array([]), k))
                continue

            # Create fake birth/death from curve changes
            births = []
            deaths = []
            for i in range(1, len(curve)):
                if curve[i] > curve[i-1]:
                    # Feature born
                    for _ in range(int(curve[i] - curve[i-1])):
                        births.append(scales[i])
                elif curve[i] < curve[i-1]:
                    # Feature died
                    for _ in range(int(curve[i-1] - curve[i])):
                        if births:
                            deaths.append(scales[i])

            # Pad deaths with infinity for surviving features
            while len(deaths) < len(births):
                deaths.append(max_edge)

            births = np.array(births[:len(deaths)])
            deaths = np.array(deaths)

            diagrams.append(PersistenceDiagram(births, deaths, k))

        return diagrams

    def persistence_entropy(
        self,
        points: np.ndarray,
        dim: int = 1,
        max_edge: Optional[float] = None
    ) -> float:
        """
        Compute persistence entropy S_T for a point cloud.

        This is the main topological observable in PIT.

        Args:
            points: (N, d) array of points
            dim: Homology dimension (0=components, 1=loops, 2=voids)
            max_edge: Maximum filtration scale

        Returns:
            Persistence entropy S_T
        """
        diagrams = self.compute_persistence(points, max_dim=dim, max_edge=max_edge)
        if dim < len(diagrams):
            return diagrams[dim].entropy()
        return 0.0


class CUSUMDetector:
    """
    Cumulative Sum (CUSUM) detector for topological transitions.

    Detects when a topological observable (like S_T) deviates
    significantly from its baseline behavior.

    In PIT, we use this to find t_topology: the time when
    topological structure begins to change.
    """

    def __init__(self, k: float = 0.5, h: float = 4.0, sigma_min: float = 0.01):
        """
        Initialize CUSUM detector.

        Args:
            k: Slack parameter (sensitivity)
            h: Threshold for detection
            sigma_min: Minimum sigma to prevent division issues
        """
        self.k = k
        self.h = h
        self.sigma_min = sigma_min

        self.mu: Optional[float] = None
        self.sigma: Optional[float] = None
        self.C_pos: float = 0.0
        self.C_neg: float = 0.0
        self.calibrated: bool = False

    def calibrate(self, baseline_data: np.ndarray) -> None:
        """
        Calibrate detector with baseline data.

        The baseline should represent the system BEFORE any transition.

        Args:
            baseline_data: Array of observations from stable regime
        """
        self.mu = np.mean(baseline_data)
        self.sigma = max(np.std(baseline_data), self.sigma_min)
        self.C_pos = 0.0
        self.C_neg = 0.0
        self.calibrated = True

    def reset(self) -> None:
        """Reset CUSUM statistics"""
        self.C_pos = 0.0
        self.C_neg = 0.0

    def update(self, value: float) -> bool:
        """
        Update detector with new observation.

        Args:
            value: New observation

        Returns:
            True if transition detected, False otherwise
        """
        if not self.calibrated:
            raise ValueError("Detector not calibrated. Call calibrate() first.")

        # Standardize
        z = (value - self.mu) / self.sigma

        # Update CUSUM statistics
        self.C_pos = max(0, self.C_pos + z - self.k)
        self.C_neg = max(0, self.C_neg - z - self.k)

        # Check for detection
        return self.C_pos > self.h or self.C_neg > self.h

    def detect(self, data: np.ndarray, baseline_fraction: float = 0.3) -> Optional[int]:
        """
        Find transition point in a complete time series.

        Args:
            data: Complete time series
            baseline_fraction: Fraction of data to use as baseline

        Returns:
            Index of detected transition, or None if not detected
        """
        baseline_idx = int(len(data) * baseline_fraction)
        baseline = data[:baseline_idx]

        self.calibrate(baseline)

        for i in range(baseline_idx, len(data)):
            if self.update(data[i]):
                return i

        return None


def delay_embedding(
    signal: np.ndarray,
    dim: int = 3,
    tau: int = 1
) -> np.ndarray:
    """
    Takens delay embedding for reconstructing phase space.

    Converts a 1D time series into a d-dimensional point cloud
    suitable for topological analysis.

    Args:
        signal: 1D time series
        dim: Embedding dimension
        tau: Time delay (in samples)

    Returns:
        (M, dim) array of embedded points
    """
    n = len(signal)
    m = n - (dim - 1) * tau

    if m <= 0:
        return np.array([])

    embedded = np.zeros((m, dim))
    for i in range(dim):
        embedded[:, i] = signal[i * tau:i * tau + m]

    return embedded


def sliding_window_entropy(
    points: np.ndarray,
    window_size: int = 30,
    step: int = 5,
    dim: int = 1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute S_T over sliding windows.

    Args:
        points: Point cloud trajectory
        window_size: Number of points per window
        step: Step between windows
        dim: Homology dimension

    Returns:
        (times, entropies) arrays
    """
    analyzer = TopologicalAnalyzer()

    times = []
    entropies = []

    for i in range(0, len(points) - window_size, step):
        window = points[i:i + window_size]
        S_T = analyzer.persistence_entropy(window, dim=dim)
        times.append(i + window_size // 2)
        entropies.append(S_T)

    return np.array(times), np.array(entropies)


# =============================================================================
# PIT Test Functions
# =============================================================================

def verify_pit(
    topological_times: np.ndarray,
    metric_times: np.ndarray,
    confidence: float = 0.95
) -> dict:
    """
    Verify the PIT principle: t_topology < t_metric

    Args:
        topological_times: Times of topological transitions (multiple trials)
        metric_times: Times of metric transitions (multiple trials)
        confidence: Confidence level for statistical test

    Returns:
        Dictionary with verification results
    """
    n_trials = min(len(topological_times), len(metric_times))

    precedes = np.sum(topological_times[:n_trials] < metric_times[:n_trials])
    rate = precedes / n_trials

    # Binomial test
    from scipy import stats
    p_value = stats.binom_test(precedes, n_trials, 0.5, alternative='greater')

    return {
        'n_trials': n_trials,
        'precedence_count': precedes,
        'precedence_rate': rate,
        'p_value': p_value,
        'pit_supported': rate > confidence,
        'mean_gap': np.mean(metric_times[:n_trials] - topological_times[:n_trials])
    }
