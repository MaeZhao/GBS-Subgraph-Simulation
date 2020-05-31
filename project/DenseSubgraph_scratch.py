# In this code I will attempt to generate the graph that was pre-genereated in the dense_graph
# tutorial code on strawberry fields (see my dsubgraph_tutorial.py file)
import distutils
from strawberryfields.apps import data, sample, subgraph, plot
import plotly
import networkx as nx
import networkx.classes.graph
import numpy as np
import random
import networkx.algorithms.operators.binary as bin
from networkx.generators.random_graphs import erdos_renyi_graph as pGraph
from networkx.readwrite.nx_yaml import write_yaml


# def initialize() -> bool:
#     """
#     [initialize()] determines whether or not process should be drawn during
#     runtime
#     :return: bool show
#     """
#     string_show: str = input("show process?")
#     if string_show == "Yes" or string_show == "yes":
#         return True;
#
#     elif string_show == "No" or string_show == "no":
#         return False;
#     else:
#         print("Input Y(y)es or N(n)o")
#         initialize();


# I will attempt to generate graphs with 0.5 probability of a edge from
# scratch:

graph = pGraph(20, 0.5)
# graph_fig = plot.graph(graph)
# graph_fig.show();

# Now I will attempt to generate a dense graph with 0.875 probability of a edge
# from scratch:
dense_graph = pGraph(10, 0.875)


# dense_graph_fig = plot.graph(dense_graph)
# dense_graph_fig.show();

# Now I will join dense_graph to graph
def gen_sub(nodes):
    """
    [gen_sub (nodes)] generates the names of the [dense_graph] nodes [nodes]
    that may be found in [union_graph].

    Assumes that [nodes] are the nodes from the [dense_graph]

    :param nodes: list
    :return s_name: str list
    """
    s_name = []
    for x in nodes:
        s_name.append("G2-" + str(x));
    return s_name


sub = gen_sub(dense_graph.nodes)  # names of the dense graph nodes
union_graph = bin.union(graph, dense_graph, rename=("G1-", "G2-"))
# unconnected_graph_fig = plot.graph(union_graph, sub)
# unconnected_graph_fig.show();

# Specify the dense subgraph R (all "G2-..." nodes)
R = union_graph.subgraph(sub)
# Specify the rest of the graph with subgraph T (all "G1-..." nodes)
T_nodes = list(union_graph.nodes)
T_nodes = [ele for ele in T_nodes if ele not in sub]
T = union_graph.subgraph(T_nodes)


# Join R to T in union_graph
def connect(rg, tg, union, steps, connect_list):
    """
    [connect(rg, Tg,union,steps, connect_list)] connects subgraphs [rg] and
    [Tg], [steps] times in graph [union]

    Assumed that [rg] and [Tg] are subgraphs of [union] and [steps] is
    greater than 0

    :param rg: graph type
    :param tg: graph type
    :param union: graph type
    :param connect_list: edge list
    :param steps: int
    :return connect_list: edge list
    """
    if (steps == 0):
        print(connect_list)
        return connect_list;
    else:
        chosen_r_node = random.choice(list(rg.nodes))
        chosen_t_node = random.choice(list(tg.nodes))
        if chosen_r_node in union.neighbors(chosen_t_node):
            return connect(rg, tg, union, steps, connect_list)
        else:
            connect_list.append((chosen_r_node, chosen_t_node))
            union.add_edge(chosen_r_node, chosen_t_node)
            return connect(rg, tg, union, steps - 1, connect_list);


joined = connect(R, T, union_graph, 8, [])


# Check whether joined is really within union_graph
def check(edge_lst, union):
    """
    [check(edge_lst, union)] checks whether or not the edge list [edge_lst]
    is within graph [union]

    :param edge_lst: edge list
    :param union: graph type
    :return: object
    """
    conjoined = False
    for x in edge_lst:
        n1 = x[0]
        n2 = x[1]
        if n1 in union.neighbors(n2):
            conjoined = True;
        else:
            conjoined = False;
    return conjoined;


correct = check(joined, union_graph)
print("Joined dense subgraph correctly: " + str(correct))


# union_graph_fig = plot.graph(union_graph, sub)
# union_graph_fig.show();

def show_all_graphs():
    """
    [show_all_graphs ()] displays all the significant graphs generated to
    get [union_graph]
    """
    # [graph]
    graph_fig = plot.graph(graph)
    graph_fig.show();
    # [dense_graph]
    dense_graph_fig = plot.graph(dense_graph)
    dense_graph_fig.show();
    # [unconnected_graph]
    unconnected_graph_fig = plot.graph(union_graph, sub)
    unconnected_graph_fig.show();
    # [union_graph]
    union_graph_fig = plot.graph(union_graph, sub)
    union_graph_fig.show();


def show_union_graph():
    """
    [show_union_graph] displays the final conjoined graph [union_graph]
    """
    union_graph_fig = plot.graph(union_graph, sub)
    union_graph_fig.show();
    

write_yaml(union_graph, 'union_graph.yaml')