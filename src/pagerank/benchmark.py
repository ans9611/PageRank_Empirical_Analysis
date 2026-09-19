"""Empirical time-complexity measurement.

The question the report asks is *how does running time grow with graph
size?*: so the independent variable must be the graph size, not the number
of repetitions. For each generator and each ``n`` we build a graph with ``n``
nodes, time ``repeats`` runs of the algorithm and keep the **minimum** (the
least noisy estimator of intrinsic cost; see ``timeit`` docs).

Run from the shell::

    pagerank-bench --sizes 50 100 200 400 800 1600 --csv results.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Callable, Iterable, List, Optional, Sequence

import networkx as nx
import numpy as np

from .core import PageRankResult, pagerank, pagerank_sparse
from .samples import GENERATORS

__all__ = ["Measurement", "time_call", "run_benchmark", "fit_power_law", "DEFAULT_SIZES"]

DEFAULT_SIZES: Sequence[int] = (25, 50, 100, 200, 400, 800, 1600)


@dataclass(frozen=True)
class Measurement:
    generator: str
    algorithm: str
    n: int
    m: int
    iterations: int
    converged: bool
    seconds: float  # best of `repeats`


def time_call(fn: Callable[[], PageRankResult], repeats: int = 5) -> tuple[float, PageRankResult]:
    """Return ``(best_seconds, last_result)`` over ``repeats`` calls of ``fn``."""
    best = float("inf")
    result = None
    for _ in range(repeats):
        t0 = perf_counter()
        result = fn()
        best = min(best, perf_counter() - t0)
    assert result is not None
    return best, result


def run_benchmark(
    sizes: Iterable[int] = DEFAULT_SIZES,
    generators: Optional[dict[str, Callable[[int], nx.Graph]]] = None,
    algorithms: Optional[dict[str, Callable[..., PageRankResult]]] = None,
    repeats: int = 5,
    **pr_kwargs,
) -> List[Measurement]:
    """Time every (generator, algorithm, n) combination.

    ``pr_kwargs`` (``d``, ``max_iter``, ``tol``) are forwarded to the
    algorithms so both are measured under identical settings.
    """
    generators = generators if generators is not None else GENERATORS
    algorithms = algorithms if algorithms is not None else {
        "python": pagerank,
        "sparse": pagerank_sparse,
    }
    out: List[Measurement] = []
    for gname, gen in generators.items():
        for n in sizes:
            G = gen(n)
            m = G.number_of_edges()
            for aname, algo in algorithms.items():
                secs, res = time_call(lambda: algo(G, **pr_kwargs), repeats=repeats)
                out.append(Measurement(gname, aname, n, m, res.iterations, res.converged, secs))
    return out


def fit_power_law(ns: Sequence[float], ts: Sequence[float]) -> tuple[float, float]:
    """Least-squares fit of ``t = c * n**k`` in log-log space.

    Returns ``(k, c)``. ``k`` near 1 supports a linear-in-n bound, near 2 a
    quadratic one.
    """
    x = np.log(np.asarray(ns, dtype=float))
    y = np.log(np.asarray(ts, dtype=float))
    k, logc = np.polyfit(x, y, 1)
    return float(k), float(np.exp(logc))


def write_csv(rows: Iterable[Measurement], path: str) -> None:
    rows = list(rows)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        w.writerows(asdict(r) for r in rows)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--sizes", type=int, nargs="+", default=list(DEFAULT_SIZES))
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--generators", nargs="+", choices=list(GENERATORS), default=list(GENERATORS))
    p.add_argument("--csv", help="write results to this CSV file")
    args = p.parse_args(argv)

    rows = run_benchmark(
        sizes=args.sizes,
        generators={k: GENERATORS[k] for k in args.generators},
        repeats=args.repeats,
    )
    if args.csv:
        write_csv(rows, args.csv)

    print(f"{'generator':24s} {'algo':7s} {'n':>6s} {'m':>7s} {'iter':>5s} {'seconds':>10s}")
    for r in rows:
        flag = "" if r.converged else " (no conv)"
        print(f"{r.generator:24s} {r.algorithm:7s} {r.n:6d} {r.m:7d} {r.iterations:5d} {r.seconds:10.5f}{flag}")

    print("\nlog-log slope of time vs n (per-iteration time, so I is factored out):")
    for gname in args.generators:
        for aname in ("python", "sparse"):
            sub = [r for r in rows if r.generator == gname and r.algorithm == aname]
            k, _ = fit_power_law([r.n for r in sub], [r.seconds / r.iterations for r in sub])
            print(f"  {gname:24s} {aname:7s} t/iter ~ n^{k:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
