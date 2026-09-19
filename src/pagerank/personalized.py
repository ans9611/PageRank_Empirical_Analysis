"""Personalized PageRank (PPR) for many sources at once.

For recommendation we need :math:`\\pi_u` for *every* user :math:`u`. Running
:func:`~pagerank.core.pagerank_sparse` once per user re-builds the matrix
each time; here the transition matrix is built once and all source columns
are iterated together as a dense ``(n, k)`` block, so each step is a single
sparse × dense product.
"""

from __future__ import annotations

from typing import Hashable, List, Optional, Sequence

import networkx as nx
import numpy as np
import scipy.sparse as sp

__all__ = ["PPRMatrix", "personalized_pagerank"]


class PPRMatrix:
    """Pre-built transition operator for repeated PPR queries on one graph."""

    def __init__(self, G: nx.Graph, weight: Optional[str] = "weight"):
        self.nodes: List[Hashable] = list(G)
        self.index = {v: i for i, v in enumerate(self.nodes)}
        n = len(self.nodes)
        D = G.to_directed() if not G.is_directed() else G
        A = sp.csr_array(nx.to_scipy_sparse_array(D, nodelist=self.nodes, weight=weight, dtype=float))
        out = np.asarray(A.sum(axis=1)).ravel()
        self.is_dangling = out == 0.0
        scale = np.where(self.is_dangling, 0.0, 1.0 / np.where(self.is_dangling, 1.0, out))
        # Store the transpose so each step is MT @ X with X of shape (n, k).
        self.MT = sp.csr_array((sp.diags(scale) @ A).T)
        self.n = n

    def run(
        self,
        sources: Sequence[Hashable],
        d: float = 0.85,
        max_iter: int = 100,
        tol: float = 1.0e-6,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """PPR from each of ``sources``.

        Returns ``(scores, iterations, converged)`` where ``scores`` has shape
        ``(len(sources), n)``: row ``i`` is the PPR vector of ``sources[i]``
        over ``self.nodes``: and the other two are per-source arrays.
        Each source's column stops being updated once it has converged.
        """
        if not 0.0 <= d < 1.0:
            raise ValueError(f"damping factor d must be in [0, 1), got {d}")
        k = len(sources)
        P = np.zeros((self.n, k))
        for j, s in enumerate(sources):
            P[self.index[s], j] = 1.0
        X = np.full((self.n, k), 1.0 / self.n)

        iterations = np.zeros(k, dtype=int)
        converged = np.zeros(k, dtype=bool)
        active = np.ones(k, dtype=bool)
        for it in range(1, max_iter + 1):
            idx = np.flatnonzero(active)
            last = X[:, idx]
            dangling_mass = d * last[self.is_dangling].sum(axis=0)  # (len(idx),)
            new = d * (self.MT @ last) + (dangling_mass + (1.0 - d)) * P[:, idx]
            X[:, idx] = new
            err = np.abs(new - last).sum(axis=0)
            iterations[idx] = it
            done = err < self.n * tol
            converged[idx[done]] = True
            active[idx[done]] = False
            if not active.any():
                break
        return X.T, iterations, converged


def personalized_pagerank(
    G: nx.Graph,
    sources: Sequence[Hashable],
    d: float = 0.85,
    max_iter: int = 100,
    tol: float = 1.0e-6,
    weight: Optional[str] = "weight",
) -> dict[Hashable, dict[Hashable, float]]:
    """PPR vectors for several sources, as ``{source: {node: score}}``."""
    op = PPRMatrix(G, weight=weight)
    X, _, _ = op.run(sources, d=d, max_iter=max_iter, tol=tol)
    return {s: dict(zip(op.nodes, X[i].tolist())) for i, s in enumerate(sources)}
