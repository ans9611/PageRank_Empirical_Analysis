"""Sample graphs used throughout the report.

Six fixed graphs of different families (path, scale-free, expander, and three
classic social networks) for convergence checks, plus size-parameterised
generators for the empirical scaling study.
"""

from __future__ import annotations

from typing import Callable, Dict

import networkx as nx

__all__ = ["SAMPLE_GRAPHS", "sample_graphs", "GENERATORS"]

# name -> (description, factory)
SAMPLE_GRAPHS: Dict[str, tuple[str, Callable[[], nx.Graph]]] = {
    "G1 path": ("Directed path graph, 36 nodes", lambda: nx.DiGraph(nx.path_graph(36))),
    "G2 scale-free": ("Scale-free directed graph, 36 nodes", lambda: nx.scale_free_graph(36, seed=0)),
    "G3 margulis-gabber-galil": (
        "Margulis–Gabber–Galil 8-regular expander, 36 nodes",
        lambda: nx.margulis_gabber_galil_graph(6),
    ),
    "G4 karate": ("Zachary's karate club (weighted), 34 nodes", nx.karate_club_graph),
    "G5 davis": ("Davis Southern women (bipartite), 32 nodes", nx.davis_southern_women_graph),
    "G6 florentine": ("Florentine families, 15 nodes", nx.florentine_families_graph),
}


def sample_graphs() -> Dict[str, nx.Graph]:
    """Build fresh copies of the six sample graphs, keyed by name."""
    return {name: factory() for name, (_, factory) in SAMPLE_GRAPHS.items()}


# Size-parameterised generators for the scaling benchmark: n -> graph.
# Chosen so that m grows linearly with n (constant average degree), which is
# what makes the O(I * (n + m)) bound show up as a straight line on a
# log-log plot.
GENERATORS: Dict[str, Callable[[int], nx.Graph]] = {
    "path": lambda n: nx.DiGraph(nx.path_graph(n)),
    "scale-free": lambda n: nx.scale_free_graph(n, seed=0),
    "erdos-renyi (k=8)": lambda n: nx.gnm_random_graph(n, 4 * n, seed=0, directed=True),
    "barabasi-albert (m=4)": lambda n: nx.barabasi_albert_graph(n, 4, seed=0),
}
