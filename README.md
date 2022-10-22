# Evaluation of the Centrality Algorithm, PageRank
* [FULL PROJECT](https://github.com/ans9611/PageRank_Empirical_Analysis/../../../../moon_project_updated.ipynb)

## Introduction
[1]The trillion dollar algorithm called, $PageRank(PR)$, is used in Google Search to rank web pages that Google's founders Sergey Brin and Larry Page developed in 1998. The PageRank algorithm measures the importance of a webpage by analyzing the quantity and quality of the links that point to it. The PR is an important member of centrality algorithms, graph algorithms. They identify the important nodes in a given graph and those nodes are defined as vertices with many direct or indirect connections. $PageRank(PR)$ finds most important vertices of a graph by analyzing the direct influence of nodes based on proportional rank.

In this project, we will demonstrated about the concepts of PageRank algorithm and its theoretical and empirical complexity.

This project demonstrates:
- The Concept of PageRank algorithm
- Implementation the PageRank algorithm and explore it on various graphs generated from Networks, python library.
- Measuring the PR complexity theoretically
- Measuring the PR complexity empirically
- PR algorithm and adjusting limitations


### Python Library Used

* Python
* pandas
* Matplotlib
* Numpy
* NetworkX


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


* [PROJECT](https://github.com/ans9611/PageRank_Empirical_Analysis/../../../../moon_project_updated.ipynb)

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

    

