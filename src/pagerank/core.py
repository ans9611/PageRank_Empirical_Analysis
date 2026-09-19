"""PageRank via power iteration.

Two implementations of the same algorithm:

* :func:`pagerank`: pure-Python, dict based. Mirrors the textbook formulation
  and is the one whose complexity is analysed in the report.
* :func:`pagerank_sparse`: scipy sparse matrix–vector product. Same result,
  much faster; used as a reference and for large graphs.

Both apply the two classic adjustments to the transition matrix:

1. *Stochasticity*: rank held by dangling nodes (no out-links) is
   redistributed uniformly, so every row of the matrix sums to 1.
2. *Primitivity*: with probability ``1 - d`` the random surfer teleports to
   a uniformly random node, which makes the chain irreducible and aperiodic
   and guarantees a unique stationary distribution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, Mapping, Optional, Sequence

import networkx as nx
import numpy as np
import scipy.sparse as sp

__all__ = ["PageRankResult", "pagerank", "pagerank_sparse"]


@dataclass(frozen=True)
class PageRankResult:
    """Outcome of a PageRank run.

    Attributes:
        scores: node -> PageRank score, summing to 1.
        iterations: number of power-iteration steps performed.
        converged: whether the L1 change fell below ``n * tol``.
        error: L1 change between the last two iterates.
    """

    scores: Dict[Hashable, float]
    iterations: int
    converged: bool
    error: float

    def top(self, k: int = 10) -> list[tuple[Hashable, float]]:
        """Return the ``k`` highest-ranked nodes as ``(node, score)`` pairs."""
        return sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)[:k]


def _teleport_vector(
    nodes: Sequence[Hashable], personalization: Optional[Mapping[Hashable, float]]
) -> np.ndarray:
    """Return the teleport distribution over ``nodes`` as a dense array.

    ``None`` means uniform. Otherwise nodes missing from the mapping get 0
    and the vector is normalised to sum to 1.
    """
    n = len(nodes)
    if personalization is None:
        return np.full(n, 1.0 / n)
    p = np.array([float(personalization.get(v, 0.0)) for v in nodes])
    if (p < 0).any():
        raise ValueError("personalization weights must be non-negative")
    total = p.sum()
    if total <= 0:
        raise ValueError("personalization must have positive total weight on the graph's nodes")
    return p / total


def _validate(d: float, max_iter: int, tol: float) -> None:
    if not 0.0 <= d < 1.0:
        raise ValueError(f"damping factor d must be in [0, 1), got {d}")
    if max_iter < 1:
        raise ValueError(f"max_iter must be >= 1, got {max_iter}")
    if tol <= 0:
        raise ValueError(f"tol must be > 0, got {tol}")


def pagerank(
    G: nx.Graph,
    d: float = 0.85,
    max_iter: int = 100,
    tol: float = 1.0e-6,
    weight: Optional[str] = "weight",
    personalization: Optional[Mapping[Hashable, float]] = None,
) -> PageRankResult:
    """Compute PageRank with pure-Python power iteration.

    Args:
        G: Any NetworkX graph. Undirected graphs are treated as directed with
           an edge in each direction.
        d: Damping factor: probability of following a link rather than
           teleporting. Must be in ``[0, 1)``.
        max_iter: Maximum number of power-iteration steps.
        tol: Convergence threshold. Iteration stops when the L1 change of the
             score vector is below ``n * tol``.
        weight: Edge attribute used as edge weight, or ``None`` to treat every
                edge as weight 1.
        personalization: Optional node -> weight mapping giving the teleport
                distribution. ``None`` is uniform (classic PageRank). A vector
                concentrated on one node (or a user's items) gives
                *Personalized* PageRank: the stationary distribution of a
                random walk that keeps restarting there. Rank held by dangling
                nodes is redistributed along the same vector.

    Returns:
        A :class:`PageRankResult`. If the method did not converge within
        ``max_iter`` steps the last iterate is still returned with
        ``converged=False``: it is never silently dropped.

    Complexity (per call, n nodes, m edges, I iterations actually run):
        time  O(n + m) setup + O(I * (n + m)) iteration
        space O(n + m) for the stochastic copy, O(n) for the score vectors
    """
    _validate(d, max_iter, tol)
    if len(G) == 0:
        return PageRankResult({}, 0, True, 0.0)

    # O(n + m): copy as directed, then scale each node's out-edges to sum to 1.
    D = G.to_directed()
    if weight is None:
        weight = "_unit_weight"
        nx.set_edge_attributes(D, 1.0, weight)
    W = nx.stochastic_graph(D, weight=weight)
    n = W.number_of_nodes()

    nodes = list(W)
    # Teleport / dangling distribution (uniform unless personalised); the
    # start vector is uniform either way.
    p = dict(zip(nodes, _teleport_vector(nodes, personalization).tolist()))
    scores: Dict[Hashable, float] = dict.fromkeys(W, 1.0 / n)
    dangling = [v for v in W if W.out_degree(v, weight=weight) == 0.0]

    error = float("inf")
    for it in range(1, max_iter + 1):
        last = scores
        scores = dict.fromkeys(last, 0.0)

        # Stochasticity adjustment: dangling mass is spread along p.
        dangling_mass = d * sum(last[v] for v in dangling)

        # O(m): each edge is visited exactly once per iteration.
        for u in last:
            for _, v, w in W.edges(u, data=weight):
                scores[v] += d * last[u] * w
        # O(n): dangling mass + primitivity adjustment (teleport mass).
        for v in scores:
            scores[v] += (dangling_mass + (1.0 - d)) * p[v]

        error = sum(abs(scores[v] - last[v]) for v in scores)
        if error < n * tol:
            return PageRankResult(scores, it, True, error)

    return PageRankResult(scores, max_iter, False, error)


def pagerank_sparse(
    G: nx.Graph,
    d: float = 0.85,
    max_iter: int = 100,
    tol: float = 1.0e-6,
    weight: Optional[str] = "weight",
    personalization: Optional[Mapping[Hashable, float]] = None,
) -> PageRankResult:
    """Same algorithm as :func:`pagerank`, using a scipy CSR matrix.

    Each iteration is one sparse mat-vec product, O(n + m), but with a much
    smaller constant than the dict implementation.
    """
    _validate(d, max_iter, tol)
    if len(G) == 0:
        return PageRankResult({}, 0, True, 0.0)

    nodes = list(G)
    n = len(nodes)
    D = G.to_directed() if not G.is_directed() else G
    A = nx.to_scipy_sparse_array(D, nodelist=nodes, weight=weight, dtype=float)
    A = sp.csr_array(A)

    out = np.asarray(A.sum(axis=1)).ravel()
    is_dangling = out == 0.0
    # Row-normalise; dangling rows stay all-zero and are handled separately.
    scale = np.where(is_dangling, 0.0, 1.0 / np.where(is_dangling, 1.0, out))
    M = sp.diags(scale) @ A  # row-stochastic (except dangling rows)

    x = np.full(n, 1.0 / n)
    p = _teleport_vector(nodes, personalization)
    error = float("inf")
    for it in range(1, max_iter + 1):
        last = x
        dangling_mass = d * last[is_dangling].sum()
        x = d * (M.T @ last) + (dangling_mass + (1.0 - d)) * p
        error = float(np.abs(x - last).sum())
        if error < n * tol:
            return PageRankResult(dict(zip(nodes, x.tolist())), it, True, error)

    return PageRankResult(dict(zip(nodes, x.tolist())), max_iter, False, error)

