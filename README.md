# Evaluation of the Centrality Algorithm, PageRank
* [FULL PROJECT](notebooks/report.ipynb)


## Introduction
[1]The trillion dollar algorithm called, $PageRank(PR)$, is used in Google Search to rank web pages that Google's founders Sergey Brin and Larry Page developed in 1998. The PageRank algorithm measures the importance of a webpage by analyzing the quantity and quality of the links that point to it. The PR is an important member of centrality algorithms, graph algorithms. They identify the important nodes in a given graph and those nodes are defined as vertices with many direct or indirect connections. $PageRank(PR)$ finds most important vertices of a graph by analyzing the direct influence of nodes based on proportional rank.

In this project, we will demonstrated about the concepts of PageRank algorithm and its theoretical and empirical complexity.

This project demonstrates:
- The Concept of PageRank algorithm
- Implementation the PageRank algorithm and explore it on various graphs generated from Networks, python library.
- Measuring the PR complexity theoretically
- Measuring the PR complexity empirically
- PR algorithm and adjusting limitations
- Personalized PageRank for many source nodes at once
- Unit tests against the NetworkX reference implementation


### Python Library Used

* Python
* NetworkX
* Numpy
* SciPy
* pandas
* Matplotlib
* pytest


## The PageRank Algorithm

[2]The PageRank algorithm gives each page a rating of its importance, which is a recursively defined measure where by a page becomes important if important pages link to it. The page rank of any page is the probability that the random surfer will land on a particular page that the surfer is more likely to end up in important pages.

The page rank of any page is the probability that the random surfer will land on a particular page that the surfer is more likely to end up in important pages. The behavior of the random surfer is an example of a Markov process, which depends only of the current state of a system. The algorithm moves moves from state to state, based on probability distribution of the likelihood of moving from each state to every other possible state. 


## Featured Notebooks/Analysis/Deliverables

### PageRank Mathematical Formula

The PageRank relies on an arbitrary probability distribution in which a person randomly clicks on links will arrive at any particular page. The probability which a person independently will continue is a damping factor $d$. PR computations require iterations through a number of pages to adjust approximate PR values to the theoretical value. The pageRank equation iteratively updates a candidate solution (rank) and arrive (converges) at an approximate solution to the same equation.

> <br>
>
> let $G = (V, E)$ be a directed graph with the set of vertices $V$ and set of edges $E$, where $E$ is subset of $V$ x $V$.
>  <br>
> Then The iteration equation of the page rank value of  $(V_i)$  is given by:
>
>$PR(V_i)$ = $(1 - d)$ + $d$ * $\sum_{n=In(Vi)}^{} PR(Vn) \over |Out(Vn)|$ <br>
<br>
> = $(1 - d)$ + $PR(V_1) \over Out(V_1)$ + ... + $PR(V_n) \over Out(V_n)$ 
>
> <br>

>   <br>
> where,
>
>- $In(V_i)$ be predecessors, set of vertices point to it; node (page) $(V_i)$ has nodes $(V_i)$ to $(V_n)$ point to it
>- $Out(V_i)$ be successors, the set of vertices that vertex $(V_i)$ points to; defined as the number of links going out of page $V$
>- $d$ is a damping factor which can be set between 0 (inclusive) and 1 (exclusive)
>- $\frac{d}{n}$ denotes random walk score
>   <br>
>   <br>

[1]The result of $PR(V_i)$ 0.4 for instance, means there is 40% chance that a person randomly surf will be directed to the node. The implementation of the classic PageRank algorithm uses an iterative method. At each iteration step, the PageRank value of all nodes in the graph are computed.

* [FULL PROJECT](notebooks/report.ipynb)


## Project Structure

```
src/pagerank/
    core.py          pagerank() in pure Python, pagerank_sparse() with SciPy
    personalized.py  PPRMatrix: Personalized PageRank for many sources at once
    samples.py       sample graphs G1~G6 and size-parameterized generators
    benchmark.py     empirical time complexity, pagerank-bench CLI
tests/               58 tests, checked against networkx.pagerank
notebooks/
    report.ipynb            the report (runs the package)
    report_v2_2022.ipynb    previous edition
```

### Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### Usage

```python
import networkx as nx
from pagerank import pagerank, pagerank_sparse, PPRMatrix

G = nx.karate_club_graph()

r = pagerank(G)                 # power iteration, d=0.85, max_iter=100, tol=1e-6
r.converged, r.iterations       # (True, 20)
r.top(3)                        # [(33, 0.1009), (0, 0.0970), (32, 0.0717)]

pagerank_sparse(G)              # same result with a scipy CSR matrix

op = PPRMatrix(G)               # Personalized PageRank, transition matrix built once
X, iters, converged = op.run([0, 33], d=0.85)   # X.shape == (2, 34)
```

`pagerank()` returns `PageRankResult(scores, iterations, converged, error)`. When the power method does not converge within `max_iter` the last iterate is returned with `converged=False`.

| **Input Argument** | **Type** | **Comment** |
|--------------------|----------|-------------|
| G | graph | input graph; undirected graphs are converted to a directed graph with two directed edges for each undirected edge |
| d | float, optional | damping factor; default=0.85 |
| max_iter | int, optional | maximum number of iterations in power method; default=100 |
| tol | float, optional | error tolerance used to check convergence; default=1e-6 |
| weight | str or None, optional | edge attribute used as weight; default="weight" |
| personalization | dict, optional | node to weight mapping for the teleport vector; default is uniform |


## Convergence Test

Six graphs generated from the NetworkX library. Our implementation and `networkx.pagerank` agree to about 1e-17.

| **Notation** | **Type of Graph** | **nodes** | **edges** | **iterations** |
|---|---|---|---|---|
| G1 | path graph, `nx.DiGraph(nx.path_graph(36))` | 36 | 70 | 46 |
| G2 | scale-free directed graph, `nx.scale_free_graph(36)` | 36 | 77 | 10 |
| G3 | Margulis-Gabber-Galil expander, `nx.margulis_gabber_galil_graph(6)` | 36 | 144 | 9 |
| G4 | Zachary's karate club (weighted) | 34 | 78 | 20 |
| G5 | Davis Southern women (bipartite) | 32 | 89 | 56 |
| G6 | Florentine families | 15 | 20 | 35 |


## Theoretical Complexity

Let $n$ be the number of nodes, $m$ the number of edges and $I$ the number of iterations.

- Converting to a directed graph and building the stochastic form is one pass over nodes and edges: $O(n + m)$
- Each iteration visits every edge once and every node once: $O(n + m)$
- Time complexity: $O(I \cdot (n + m))$
- Space complexity: $O(n + m)$ for the stochastic copy of the graph and $O(n)$ for the rank vectors

$O(I \cdot n^2)$ holds only for dense graphs where $m = \Theta(n^2)$. The graphs used in this project are sparse.


## Empirical Time Complexity

```bash
pagerank-bench --sizes 50 100 200 400 800 1600 --csv results.csv
```

For each generator, graphs with $n = 25, 50, \dots, 1600$ nodes and constant average degree are built, timed, and the per-iteration time is fitted with $t = c \cdot n^k$ in log-log space.

| generator | $k$ (pure Python) | $k$ (sparse) |
|---|---|---|
| path | 1.28 | 0.89 |
| scale-free | 1.09 | 0.57 |
| Erdos-Renyi | 1.02 | 0.56 |
| Barabasi-Albert | 1.08 | 0.95 |

$k$ is close to 1 for every generator, which matches $O(I \cdot (n + m))$ with $m \propto n$. The sparse implementation is 5 to 20 times faster; at these sizes its time is mostly the matrix construction, which is why its slope is below 1.

The number of iterations $I$ depends on the second eigenvalue of the transition matrix, not on $n$. G1 and G5 need about 50 iterations while the expander G3 needs 9.


## Personalized PageRank

With a personalization vector $p$, the random surfer teleports to nodes in proportion to $p$ instead of uniformly, and the rank held by dangling nodes is redistributed along $p$ as well.

$PR = (1 - d) \, p + d \, P^T PR$

`PPRMatrix` builds the transition matrix once and iterates all source nodes together as one dense block, so each iteration is a single sparse times dense product. On a 20,000-node Barabasi-Albert graph, PPR for 500 sources takes about 1 second, compared with about 220 seconds one source at a time.


## References


[1]Wikipedia Contributors, PageRank, Wikipedia. (2022).<br> https://en.wikipedia.org/wiki/PageRank (accessed July 24, 2022).<br>
<br>
[2]Graph generators — NetworkX 2.8.5 documentation, Networkx.org. (2019).<br> https://networkx.org/documentation/stable/reference/generators.html (accessed July 24, 2022).<br>
<br>
[3]pagerank — NetworkX 2.8.5 documentation, Networkx.org. (2022).<br> https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html (accessed July 24, 2022).<br>
<br>
[4]L. Page, S. Brin, R. Motwani, T. Winograd, The PageRank Citation Ranking: Bringing Order to the Web. - Stanford InfoLab Publication Server, Stanford.edu. (1999).<br> https://doi.org/http://ilpubs.stanford.edu:8090/422/1/1999-66.pdf.<br>
<br>
[5]E. Guven, module05_ds, Jhu.edu. (2022).<br> https://jhu.instructure.com/courses/13110/pages/module-5-readings?module_item_id=1077894 (accessed July 24, 2022).<br>

[6]R. Mihalcea, P. Tarau, TextRank: Bringing Order into Texts, n.d.<br> https://digital.library.unt.edu/ark:/67531/metadc30962/m2/1/high_res_d/Mihalcea-2004-TextRank-Bringing_Order_into_Texts.pdf.

[7]
path_graph — NetworkX 2.8.5 documentation, Networkx.org. (2022).<br> https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.path_graph.html#networkx.generators.classic.path_graph (accessed July 26, 2022).<br>

[8]
path_graph — NetworkX 2.8.5 documentation, Networkx.org. (2022).<br> https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.path_graph.html#networkx.generators.classic.path_graph (accessed July 26, 2022).<br>

[9]
scale_free_graph — NetworkX 2.8.5 documentation, Networkx.org. (2022). https://networkx.org/documentation/stable/reference/generated/networkx.generators.directed.scale_free_graph.html (accessed July 26, 2022).<br>

[10]
karate_club_graph — NetworkX 2.8.5 documentation, Networkx.org. (2022).<br> https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.karate_club_graph.html#networkx.generators.social.karate_club_graph (accessed July 26, 2022).<br>

[11]
karate_club_graph — NetworkX 2.8.5 documentation, Networkx.org. (2022).<br> https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.karate_club_graph.html#networkx.generators.social.karate_club_graph (accessed July 26, 2022).<br>

[12]
davis_southern_women_graph — NetworkX 2.8.5 documentation, Networkx.org. (2022)<br>. https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.davis_southern_women_graph.html (accessed July 26, 2022).<br>

[13]
florentine_families_graph — NetworkX 2.8.5 documentation, Networkx.org. (2022).<br> https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.florentine_families_graph.html (accessed July 26, 2022).<br>

[14]
B. Ali, School of Education, Culture and Communication Division of Applied Mathematics MASTER (1 YEAR) THESIS IN MATHEMATICS / APPLIED MATHEMATICS<br> A comparison of a Lazy PageRank and variants for common graph structures, n.d.<br> https://mdh.diva-portal.org/smash/get/diva2:1179590/FULLTEXT01.pdf.<br>

    

