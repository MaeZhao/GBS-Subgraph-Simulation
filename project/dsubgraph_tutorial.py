# @formatter:on
"""Dense Subgraphs Strawberry Fields Tutorial from:
https://strawberryfields.readthedocs.io/en/stable/tutorials_apps/run_tutorial_dense.html

The graphs specified in this tutorial are pre-generated with the first graph
of 20 nodes is created with edge probability of 0.5. The second planted
graph is generated with edge probability of 0.875. The graphs are connected
via 8 randomly selected vertices.

Below displays the tutorial code + a few lines of my custom clarifying code and
notes
"""
import networkx as nx
import plotly
from strawberryfields.apps import data, sample, subgraph, plot

# First the pre-generated graph data is imported from StrawberryFields:
planted = data.Planted()
# pl_graph = the selected graph with planted dense sub graph:
pl_graph = nx.to_networkx_graph(planted.adj)
pl_fig = plot.graph(pl_graph)
pl_fig.show()

# postselected = postselecting samples by imposing a minimum and maximum
# number of clicks (in this case 16 minimum clicks and 30 maximum clicks)
postselected = sample.postselect(planted, 16, 30)
samples = sample.to_subgraphs(postselected, pl_graph)
print(len(samples))

sub = list(range(20, 30))
plot_graph = plot.graph(pl_graph, sub)
plotly.offline.plot(plot_graph, filename="planted.html")

dense = subgraph.search(samples, pl_graph, 8, 16,
                        max_count=3)  # we look at top 3 densest subgraphs
for k in range(8, 17):
    print(dense[k][0])  # print only the densest dense_graph of each size
densest_8 = plot.graph(pl_graph, dense[8][0][1])
densest_16 = plot.graph(pl_graph, dense[12][0][1])

plotly.offline.plot(densest_8, filename="densest_8.html")
plotly.offline.plot(densest_16, filename="densest_16.html")
