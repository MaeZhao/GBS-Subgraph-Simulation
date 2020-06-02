# In this code I will attempt to generate the graph that was pre-genereated
# in the dense_graph tutorial code on strawberry fields (see my
# tutorial.py file)
import distutils
from functools import reduce

from strawberryfields.apps import data, sample, subgraph, plot
import plotly
import networkx as nx
import networkx.classes.graph
import numpy as np
import random
import networkx.algorithms.operators.binary as bin
from networkx.generators.random_graphs import erdos_renyi_graph as pGraph
from networkx.readwrite.nx_yaml import write_yaml
import multiprocessing as mp
import pickle
import time
import warnings
from multiprocessing import Queue, Process

import networkx as nx
from networkx.readwrite.nx_yaml import read_yaml
from strawberryfields.apps import sample


def initialize() -> bool:
	"""
	[initialize()] determines whether or not process should be drawn during
	runtime
	:return: bool show
	"""
	string_show: str = input("show process?")
	if string_show == "Yes" or string_show == "yes":
		return True
	elif string_show == "No" or string_show == "no":
		return False
	else:
		print("Invalid Input--Input Y(y)es or N(n)o")


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
		s_name.append("G2-" + str(x))
	return s_name


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
	if steps == 0:
		print(connect_list)
		return connect_list
	else:
		chosen_r_node = random.choice(list(rg.nodes))
		chosen_t_node = random.choice(list(tg.nodes))
		if chosen_r_node in union.neighbors(chosen_t_node):
			return connect(rg, tg, union, steps, connect_list)
		else:
			connect_list.append((chosen_r_node, chosen_t_node))
			union.add_edge(chosen_r_node, chosen_t_node)
			return connect(rg, tg, union, steps - 1, connect_list)


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
			conjoined = True
		else:
			conjoined = False
	return conjoined


def show_all_graphs(graph, dense_graph, union_graph, sub):
	"""
	[show_all_graphs ()] displays all the significant graphs generated to
	get [union_graph]
	"""
	# [graph]
	graph_fig = plot.graph(graph)
	graph_fig.show()
	# [dense_graph]
	dense_graph_fig = plot.graph(dense_graph)
	dense_graph_fig.show()
	# [unconnected_graph]
	unconnected_graph_fig = plot.graph(union_graph, sub)
	unconnected_graph_fig.show()
	# [union_graph]
	union_graph_fig = plot.graph(union_graph, sub)
	union_graph_fig.show()


def show_union_graph(union_graph, sub):
	"""
	[show_union_graph] displays the final conjoined graph [union_graph]
	"""
	union_graph_fig = plot.graph(union_graph, sub)
	union_graph_fig.show()


if __name__ == '__main__':
	# initialize()
	manager = mp.Manager()
	
	
	def build_graph(show_steps=False, show_union=False):
		# I will attempt to generate graphs with 0.5 probability of a edge from
		# scratch:
		graph = pGraph(20, 0.5)
		
		# Now I will attempt to generate a dense graph with 0.875 probability of
		# a edge from scratch:
		dense_graph = pGraph(10, 0.875)
		
		# Now I will join dense_graph to graph
		sub = gen_sub(dense_graph.nodes)  # names of the dense graph nodes
		union_graph = bin.union(graph, dense_graph, rename=("G1-", "G2-"))
		
		# Specify the dense subgraph R (all "G2-..." nodes)
		R = union_graph.subgraph(sub)
		# Specify the rest of the graph with subgraph T (all "G1-..." nodes)
		t_nodes = list(union_graph.nodes)
		t_nodes = [ele for ele in t_nodes if ele not in sub]
		t = union_graph.subgraph(t_nodes)
		
		# Join R to T in union_graph
		joined = connect(R, t, union_graph, 8, [])
		# Check whether joined is really within union_graph
		correct = check(joined, union_graph)
		print("Joined dense subgraph correctly: " + str(correct))
		if show_steps:
			show_all_graphs(graph, dense_graph, union_graph, sub)
		if show_union:
			show_union_graph(union_graph, sub)
		return union_graph
	
	
	def pool_graph_gen(num_graphs, pkl_dir='data/BLT/master/BLT-all.pkl'):
		graph_lst = manager.list()
		pool = mp.Pool()
		
		# saves the html and pkl data of individual graphs
		def save_result(result):
			graph_lst.append(result)
			# save pkl data
			ind = len(graph_lst)
			filename = 'data/BLT/BLT-' + str(ind) + '.pkl'
			print("saving  ", filename)
			outfile = open(filename, 'wb')
			pickle.dump(result, outfile)
			outfile.close()
			# save html of graph
			result = plot.graph(result)
			html_dir = 'built-graph-htmls/BLT-' + str(ind) + '.html'
			plotly.offline.plot(result, filename=html_dir, auto_open=False)
		
		# generates graphs in parallel
		for i in range(num_graphs):
			pool.apply_async(build_graph,
			                 args=(),
			                 callback=save_result)
		# saves data of all graphs a pkl
		print("saving ", pkl_dir)
		ofile = open(pkl_dir, 'wb')
		pickle.dump(graph_lst, ofile)
		ofile.close()
		pool.close()
		pool.join()
		
		# Check for uniqueness: if true, then all unique, false, otherwise
		def unique_report(lst):
			u = len(set(lst)) == len(lst)
			return u
		
		unique = unique_report(graph_lst)
		print("UNIQUE: ", unique)
		return
	
	pool_graph_gen(3)
