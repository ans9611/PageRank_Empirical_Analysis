import networkx as nx
import pytest

from pagerank.benchmark import Measurement, fit_power_law, run_benchmark, time_call, main
from pagerank.core import pagerank


def test_time_call_returns_min_and_result():
    secs, res = time_call(lambda: pagerank(nx.path_graph(10)), repeats=3)
    assert secs >= 0 and res.converged


def test_run_benchmark_varies_graph_size():
    rows = run_benchmark(sizes=[10, 20], generators={"path": lambda n: nx.path_graph(n)}, repeats=1)
    assert [r.n for r in rows if r.algorithm == "python"] == [10, 20]
    assert all(isinstance(r, Measurement) for r in rows)
    assert {r.algorithm for r in rows} == {"python", "sparse"}


def test_fit_power_law_recovers_exponent():
    ns = [10, 20, 40, 80]
    k, c = fit_power_law(ns, [3.0 * n**2 for n in ns])
    assert k == pytest.approx(2.0)
    assert c == pytest.approx(3.0)


def test_cli_runs(capsys, tmp_path):
    out = tmp_path / "r.csv"
    assert main(["--sizes", "10", "20", "--repeats", "1", "--generators", "path", "--csv", str(out)]) == 0
    assert "t/iter ~ n^" in capsys.readouterr().out
    assert out.read_text().startswith("generator,algorithm,n,m,")
