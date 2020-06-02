from shutil import copyfile

import dload as dload
from strawberryfields.apps import data, sample, subgraph, plot
from os import chdir as cd
import plotly
import time
import networkx as nx
import networkx.classes.graph
import numpy as np
import random
import networkx.algorithms.operators.binary as bin
from networkx.generators.random_graphs import erdos_renyi_graph as pGraph
from networkx.readwrite.nx_yaml import write_yaml
import pickle
import networkx as nx
import numpy as np
import multiprocess as mp
from multiprocessing import Process, Pool, Value
import threading as threading
from networkx.readwrite.nx_yaml import read_yaml

adj = nx.to_numpy_array(read_yaml('union_graph.yaml'))
threads = []
graph = nx.Graph(adj)

filename = 'SAVE-DATA.pkl'
infile = open(filename, 'rb')
subgraph_dict = pickle.load(infile)
infile.close()


# def try_samp(maxSample):
# 		try:
# 			sample.sample(adj, 8, maxSample, threshold=False)
# 		except RuntimeWarning:
# 			print("ERROR RESAMPLE")
# 			try_samp()
#
#
# subgraphs = try_samp(5)


ind = 1
for i in subgraph_dict:
	subgraph = i["subgraph"]
	subgraph = subgraph[0]
	temp_sub = plot.graph(graph, subgraph)
	save_dir = 'sample-htmls/' + str(ind) + '.html'
	ind += 1
	plotly.offline.plot(temp_sub, filename=save_dir, )

# time.sleep(1)
#
# copyfile('{}/{}.html'.format(dload, ind),
#          '{}/{}.html'.format(save_dir, ind))
