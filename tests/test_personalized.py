import networkx as nx
import numpy as np
import pytest

from pagerank import pagerank_sparse
from pagerank.personalized import PPRMatrix, personalized_pagerank


def test_batched_matches_single_source():
    G = nx.karate_club_graph()
    sources = [0, 5, 33]
    batched = personalized_pagerank(G, sources, tol=1e-10, max_iter=1000)
    for s in sources:
        single = pagerank_sparse(G, personalization={s: 1.0}, tol=1e-10, max_iter=1000).scores
        for v in G:
            assert batched[s][v] == pytest.approx(single[v], abs=1e-9)


def test_batched_matches_networkx_with_dangling():
    G = nx.DiGraph([(0, 1), (1, 2), (0, 3), (3, 4)])
    op = PPRMatrix(G)
    X, its, conv = op.run([0, 3], tol=1e-10, max_iter=1000)
    assert conv.all()
    for i, s in enumerate([0, 3]):
        ref = nx.pagerank(G, personalization={s: 1.0}, tol=1e-10, max_iter=1000)
        for v in G:
            assert X[i, op.index[v]] == pytest.approx(ref[v], abs=1e-8)


def test_rows_are_distributions():
    G = nx.barabasi_albert_graph(300, 3, seed=0)
    X, _, conv = PPRMatrix(G).run(list(range(50)))
    assert X.shape == (50, 300)
    assert conv.all()
    assert np.allclose(X.sum(axis=1), 1.0)
    assert (X >= 0).all()


def test_per_source_iteration_counts_and_early_stop():
    # Source on an expander converges fast, source on a long path slowly:
    # iterations must be tracked per source.
    G = nx.disjoint_union(nx.Graph(nx.margulis_gabber_galil_graph(6)), nx.path_graph(36))
    _, its, conv = PPRMatrix(G).run([0, 36 + 17])
    assert conv.all()
    assert its[0] < its[1]


def test_reuse_operator_across_damping_factors():
    op = PPRMatrix(nx.florentine_families_graph())
    lo, _, _ = op.run(["Medici"], d=0.1)
    hi, _, _ = op.run(["Medici"], d=0.9)
    i = op.index["Medici"]
    assert lo[0, i] > hi[0, i]  # low d keeps mass at the source
