import math

import networkx as nx
import pytest

from pagerank import pagerank, pagerank_sparse, sample_graphs

IMPLS = [pagerank, pagerank_sparse]


@pytest.mark.parametrize("impl", IMPLS)
@pytest.mark.parametrize("name", list(sample_graphs()))
def test_matches_networkx_reference(impl, name):
    G = sample_graphs()[name]
    # Slow-mixing graphs (path, bipartite) need more than 100 steps for 1e-10.
    ours = impl(G, tol=1e-10, max_iter=1000).scores
    ref = nx.pagerank(G, tol=1e-10, max_iter=1000)
    assert ours.keys() == ref.keys()
    for v in G:
        assert ours[v] == pytest.approx(ref[v], abs=1e-8)


@pytest.mark.parametrize("impl", IMPLS)
def test_scores_form_distribution(impl):
    r = impl(nx.karate_club_graph())
    assert r.converged
    assert sum(r.scores.values()) == pytest.approx(1.0)
    assert all(s > 0 for s in r.scores.values())


@pytest.mark.parametrize("impl", IMPLS)
def test_two_implementations_agree(impl):
    G = nx.scale_free_graph(200, seed=1)
    a = pagerank(G, tol=1e-10).scores
    b = pagerank_sparse(G, tol=1e-10).scores
    for v in G:
        assert a[v] == pytest.approx(b[v], abs=1e-9)


@pytest.mark.parametrize("impl", IMPLS)
def test_empty_graph(impl):
    r = impl(nx.DiGraph())
    assert r.scores == {} and r.converged and r.iterations == 0


@pytest.mark.parametrize("impl", IMPLS)
def test_dangling_nodes_are_handled(impl):
    # 0 -> 1 -> 2, node 2 has no out-links: its rank must be redistributed,
    # not lost, so the total still sums to 1.
    G = nx.DiGraph([(0, 1), (1, 2)])
    r = impl(G)
    assert r.converged
    assert sum(r.scores.values()) == pytest.approx(1.0)
    assert r.scores[2] > r.scores[1] > r.scores[0]


@pytest.mark.parametrize("impl", IMPLS)
def test_non_convergence_returns_last_iterate(impl):
    # The original implementation returned None here.
    G = nx.davis_southern_women_graph()
    r = impl(G, max_iter=2)
    assert not r.converged
    assert r.iterations == 2
    assert len(r.scores) == len(G)
    assert sum(r.scores.values()) == pytest.approx(1.0)


@pytest.mark.parametrize("impl", IMPLS)
def test_weight_none_ignores_edge_weights(impl):
    G = nx.karate_club_graph()  # has 'weight' attributes
    unweighted = impl(G, weight=None).scores
    ref = nx.pagerank(G, weight=None)
    for v in G:
        assert unweighted[v] == pytest.approx(ref[v], abs=1e-6)
    # and it must differ from the weighted answer
    weighted = impl(G).scores
    assert any(not math.isclose(weighted[v], unweighted[v], abs_tol=1e-6) for v in G)


@pytest.mark.parametrize("impl", IMPLS)
def test_undirected_graph_treated_as_bidirectional(impl):
    G = nx.path_graph(5)
    r = impl(G)
    # symmetric graph -> symmetric ranks
    assert r.scores[0] == pytest.approx(r.scores[4])
    assert r.scores[1] == pytest.approx(r.scores[3])


@pytest.mark.parametrize("impl", IMPLS)
@pytest.mark.parametrize("kwargs", [dict(d=1.0), dict(d=-0.1), dict(max_iter=0), dict(tol=0)])
def test_invalid_parameters(impl, kwargs):
    with pytest.raises(ValueError):
        impl(nx.path_graph(3), **kwargs)


def test_top():
    r = pagerank(nx.karate_club_graph())
    top = r.top(3)
    assert [v for v, _ in top] == [33, 0, 32]
    assert top[0][1] >= top[1][1] >= top[2][1]


# --- personalization -------------------------------------------------------

@pytest.mark.parametrize("impl", IMPLS)
def test_personalization_matches_networkx(impl):
    G = nx.karate_club_graph()
    pers = {0: 1.0, 33: 3.0}  # un-normalised on purpose
    ours = impl(G, personalization=pers, tol=1e-10, max_iter=1000).scores
    ref = nx.pagerank(G, personalization=pers, tol=1e-10, max_iter=1000)
    for v in G:
        assert ours[v] == pytest.approx(ref[v], abs=1e-8)


@pytest.mark.parametrize("impl", IMPLS)
def test_personalization_with_dangling_nodes_matches_networkx(impl):
    # 2 is dangling; its mass must flow back to the personalization vector.
    G = nx.DiGraph([(0, 1), (1, 2), (0, 3)])
    pers = {0: 1.0}
    ours = impl(G, personalization=pers, tol=1e-10, max_iter=1000).scores
    ref = nx.pagerank(G, personalization=pers, tol=1e-10, max_iter=1000)
    for v in G:
        assert ours[v] == pytest.approx(ref[v], abs=1e-8)
    assert sum(ours.values()) == pytest.approx(1.0)


@pytest.mark.parametrize("impl", IMPLS)
def test_personalized_rank_concentrates_near_source(impl):
    G = nx.path_graph(20)
    r = impl(G, personalization={0: 1.0}, d=0.5)
    scores = [r.scores[i] for i in range(20)]
    # decays away from the source; the far tail sits below tol so is not checked
    head = scores[:8]
    assert head == sorted(head, reverse=True)
    assert scores[0] > 10 * scores[19]


@pytest.mark.parametrize("impl", IMPLS)
def test_uniform_personalization_equals_classic(impl):
    G = nx.florentine_families_graph()
    classic = impl(G, tol=1e-10, max_iter=1000).scores
    uniform = impl(G, personalization={v: 7.0 for v in G}, tol=1e-10, max_iter=1000).scores
    for v in G:
        assert classic[v] == pytest.approx(uniform[v], abs=1e-9)


@pytest.mark.parametrize("impl", IMPLS)
@pytest.mark.parametrize("pers", [{}, {"not-a-node": 1.0}, {0: -1.0}])
def test_invalid_personalization(impl, pers):
    with pytest.raises(ValueError):
        impl(nx.path_graph(3), personalization=pers)
