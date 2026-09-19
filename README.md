# PageRank: Implementation and Complexity Analysis

An implementation of PageRank from scratch, with a theoretical and empirical
analysis of its running time.

* Report: [`notebooks/report.ipynb`](notebooks/report.ipynb)
* Code: [`src/pagerank/`](src/pagerank/)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Usage

```python
import networkx as nx
from pagerank import pagerank, pagerank_sparse, PPRMatrix

G = nx.karate_club_graph()

r = pagerank(G)            # pure-Python power iteration
r.converged, r.iterations  # (True, 20)
r.top(3)                   # [(33, 0.1009), (0, 0.0970), (32, 0.0717)]

pagerank_sparse(G)         # same algorithm with a scipy sparse matrix

# Personalized PageRank for many sources at once
op = PPRMatrix(G)
X, iters, converged = op.run([0, 33], d=0.85)   # X.shape == (2, 34)
```

`pagerank(G, d=0.85, max_iter=100, tol=1e-6, weight="weight", personalization=None)`
returns a `PageRankResult(scores, iterations, converged, error)`. If the power
method does not converge within `max_iter`, the last iterate is returned with
`converged=False`.

Scaling benchmark:

```bash
pagerank-bench --sizes 50 100 200 400 800 1600 --csv results.csv
```

## Algorithm

Let $G=(V,E)$ be a directed graph, $n=|V|$, and $d$ the damping factor. The
PageRank of node $v$ is the fixed point of

$$PR(v) = \frac{1-d}{n} + d \sum_{u \in In(v)} \frac{PR(u)}{|Out(u)|}$$

computed by power iteration from the uniform vector. Two adjustments make the
fixed point unique:

1. Stochasticity: rank held by dangling nodes (no out-links) is redistributed
   uniformly, so every row of the transition matrix sums to 1.
2. Primitivity: with probability $1-d$ the surfer jumps to a random node, which
   makes the chain irreducible and aperiodic.

With a personalization vector, both the jump and the dangling redistribution
follow that vector instead of the uniform one.

## Complexity

For $n$ nodes, $m$ edges and $I$ iterations:

| | time | space |
|---|---|---|
| setup (directed copy, row normalization) | $O(n+m)$ | $O(n+m)$ |
| one iteration | $O(n+m)$ | $O(n)$ |
| total | $O(I \cdot (n+m))$ | $O(n+m)$ |

The benchmark uses generators with constant average degree, so $m \propto n$.
The log-log slope of per-iteration time against $n$ is close to 1 for every
generator. $I$ depends on the spectral gap of the graph rather than on $n$: the
path graph and the bipartite Davis graph need about 50 iterations, the
Margulis-Gabber-Galil expander fewer than 10.

## References

1. L. Page, S. Brin, R. Motwani, T. Winograd. The PageRank Citation Ranking: Bringing Order to the Web. Stanford InfoLab, 1999.
2. A. N. Langville, C. D. Meyer. Google's PageRank and Beyond. Princeton University Press, 2006.
3. R. Mihalcea, P. Tarau. TextRank: Bringing Order into Texts. EMNLP 2004.
4. NetworkX documentation: [pagerank](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html), [graph generators](https://networkx.org/documentation/stable/reference/generators.html).
5. Wikipedia: [PageRank](https://en.wikipedia.org/wiki/PageRank).
6. E. Guven. Module 5 course notes, JHU EN.605, 2022.
