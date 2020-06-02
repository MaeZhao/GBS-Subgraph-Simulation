# This code is used to generate samples of a graph

import multiprocessing as mp
import pickle
import time
import warnings
from multiprocessing import Queue, Process

import networkx as nx
from networkx.readwrite.nx_yaml import read_yaml
from strawberryfields.apps import sample

# Makes a sample of a [adj_mat]--if error occurs simply resamples. The size of
# sample is determined by [cluster_size]
def make_sample(adj_mat, queue, cluster_size):
	with warnings.catch_warnings():
		warnings.simplefilter("error")
		try:
			sampling = sample.sample(adj_mat, 8, cluster_size, threshold=True)
			if not sampling:
				make_sample(adj_mat, queue)
				return
			else:
				queue.put(sampling)
				return
		except RuntimeWarning:
			print("ERROR RESAMPLE")
			make_sample(adj_mat, queue)
			return


# Used for pool sampling--needed to create a temporary queue used for
# calling [make_sample()]
def pool_make_sample(adj, clust_size):
	# print("Sampling cluster:  ", num)
	temp_queue = Queue()
	make_sample(adj, temp_queue, clust_size)
	# print("Done processing cluster: ", num)
	data_nodes = temp_queue.get()
	return data_nodes


# Removes empty lists from a list of lists [lsts] (i.e. our list of subgraph
# samples)
def remove_empty(lst):
	try:
		ret = lst.remove([])
		return remove_empty(ret)
	except ValueError:
		return lst


# USING MULTIPROCESSING (USE INSTEAD OF POOLING)--PICK EITHER OR METHODS
# TO COMPUTE SAMPLES (pick based on time)
def multiproc_sub_samp(graph, samp_cluster, clust_size):
	save_lst = manager.list()
	tm_i = time.time()
	jobs = []
	for i in range(samp_cluster):
		queue2 = Queue()
		# print("Initializing process", (i + 1), " of ", samp_cluster)
		# print("    Queue ", (i + 1), " empty: ", queue2.empty())
		p = Process(target=make_sample, name=str(i + 1),
		            args=(adjacency_graph, queue2, clust_size,))
		jobs.append(p)
		p.start()
		p.join()
		# print("    Queue ", (i + 1), " empty: ", queue2.empty())
		v = queue2.get()
		v = sample.postselect(v, 16, 30)
		save_lst.extend(v)
	while len(jobs) > 0:
		# print("...", mp.active_children())
		jobs = [job for job in jobs if job.is_alive()]
		time.sleep(1)
	save_lst = sample.to_subgraphs(save_lst, graph)
	# print("FINAL processing MATRIX: ", save_lst)
	multiprocess_time = time.time() - tm_i
	save_lst = remove_empty(save_lst)
	return save_lst, multiprocess_time


# POOLING TECHNIQUE (USE INSTEAD OF MULTIPROCESSING)--PICK EITHER OR METHODS
# TO COMPUTE SAMPLES (pick based on time)
def pool_sub_samp(graph, samp_cluster, clust_size):
	save_lst = manager.list()
	tp_i = time.time()
	pool = mp.Pool()
	
	def compile_result(result):
		save_lst.extend(result)
	
	for i in range(samp_cluster):
		# t = mp.Value(i, 'i')
		# print("starting pool ", (i + 1), " of ", samp_cluster)
		pool.apply_async(pool_make_sample,
		                 args=(adjacency_graph, clust_size),
		                 callback=compile_result)
	pool.close()
	pool.join()
	save_lst = sample.to_subgraphs(save_lst, graph)
	pooling_time = time.time() - tp_i
	# print("FINAL pool MATRIX: ", save_lst)
	return save_lst, pooling_time


def init_graph_sampling(adj_graph, max_samples=50, multi_target="multiprocess",
                        sample_size=10):
	if max_samples < sample_size:
		raise ValueError("maxSample must be larger than sample_size")
	
	graph = nx.Graph(adj_graph)
	num_clusters = int(max_samples / sample_size)
	
	if not (max_samples % sample_size == 0):
		raise UserWarning("max_samples should be divisible by sample_size, "
		                  "max_samples is set to " +
		                  str(sample_size * sample_size) +
		                  ", instead. Change sample_size size to "
		                  "accommodate max_samples")
	
	if multi_target == "multiprocess":
		print("MULTIPROCESSING ", max_samples, " SAMPLES IN", sample_size,
		      "CLUSTERS")
		ret_data = multiproc_sub_samp(graph, num_clusters, sample_size)
		save_lst = ret_data[0]
		elapsed_time = ret_data[1]
	elif multi_target == "pool":
		print("POOLING ", max_samples, " SAMPLES IN", sample_size,
		      "CLUSTERS")
		ret_data = pool_sub_samp(graph, num_clusters, sample_size)
		save_lst = ret_data[0]
		elapsed_time = ret_data[1]
	else:
		raise ValueError("multi_target is must be either 'multiprocess' or "
		                 "'pool'")
	return save_lst, graph, elapsed_time


if __name__ == '__main__':
	adjacency_graph = nx.to_numpy_array(read_yaml('union_graph.yaml'))
	manager = mp.Manager()
	maxSamp = 100
	sampSize = 10
	# SAMPLING ONLY DEPENDS ON CALLING init_graph_sampling()
	# CAN CHOOSE TO POOL OR MULTIPROCESS LARGE SAMPLES
	#   MULTIPROCESS EX:
	sub_data_m = init_graph_sampling(adjacency_graph, max_samples=maxSamp,
	                                 multi_target="multiprocess",
	                                 sample_size=sampSize)
	save_m = (sub_data_m[0], sub_data_m[1])  # (subgraph list * graph)
	total_time_m = sub_data_m[2]
	print("MULTIPROCESSING TIME: ", total_time_m)
	
	filename = 'SAMPLE_DATA_' + str(maxSamp) + '_M.pkl'
	print("saving to ", filename)
	outfile = open(filename, 'wb')
	pickle.dump(save_m, outfile)
	outfile.close()
	
	#   POOL EX:
	sub_data_p = init_graph_sampling(adjacency_graph, max_samples=maxSamp,
	                                 multi_target="pool",
	                                 sample_size=sampSize)
	save_p = (sub_data_p[0], sub_data_m[1])  # (subgraph list * graph)
	total_time_p = sub_data_p[2]
	print("POOLING TIME: ", total_time_m)
	
	filename = 'SAMPLE_DATA_' + str(maxSamp) + '_P.pkl'
	print("saving to ", filename)
	outfile = open(filename, 'wb')
	pickle.dump(save_p, outfile)
	outfile.close()
	print("done with parallel")
	print("data loaded")

# OLD CODE:
# ___________________________________________________________________________
# 	def foldl(func, acc, xs):
# 		return functools.reduce(func, xs, acc)
# print("starting NON THREAD")
# ts = time.time()
#	# save_length = len(save)
# rand_int = random.randrange(0, (save_length - 1), )
# rand_node = save[0]
# print("FINAL LENGTH ", save_length)
# print("total time with thread ", total_time)
# def try_samp():
# 	try:
# 		s = sample.sample(g_adj, 8, maxSample, threshold=False)
# 		return s
# 	except RuntimeWarning:
# 		print("ERROR RESAMPLE")
# 		try_samp()
#
# try_samp()
# tfin = time.time()
# total_ts = tfin - ts
# print("total time without thread ", total_ts)

# main_thread = threading.Thread(None, target=classic_gen_time_sample1,
#                                name="1",
#                                args=[maxSample, queue1],
#                                daemon=True, )
# print("running THREADED")
# total_t1 = time.time()
# main_thread.start()
# main_thread.join()
# save = queue1.get()
# tf = time.time()
# total_time = tf - total_t1
# # Debug
# save_length = len(save)
# rand_int = random.randrange(0, (save_length - 1), )
# rand_node = save[0]
# print("SAVE LENGTH ", save_length)
# print("total time with thread ", total_time)
#
# filename = 'SAVE-DATA1.pkl'
# print("saving to ", filename)
# outfile = open(filename, 'wb')
# pickle.dump(save, outfile)
# outfile.close()
# print("done with parallel")
# print("data loaded")

# dill.dump_session("sample_pregen_dat.pkl")
# runInParallel (process_thread_1, (5),
#                process_thread_2, (5))

# t0 = time.time()
# thread1.start()
# thread2.start()
# thread1.join()
# tf1 = time.time()
#
# thread2.join()
# tf2 = time.time()
#
# threaded_time = tf1 - t0
# no_thread_time = tf2 - t0
# Saving our time x sample size data:

# Samples all 20 subgraphs
# classic_time_sample_data = classic_gen_time_Sample1(2, [])

# classic_time_sample_data1 = queue1.get()

# Samples all 20 subgraphs
# classic_time_sample_data = classic_gen_time_Sample2(2, [])

# classic_time_sample_data2 = queue2.get()

# To load data:
# dill.load_session("sample_pregen_dat.out")


# def classic_gen_time_sample1(max_samp, queue):
# 	def thread_samples(mSamp):
# 		print(str(mSamp))
# 		temp_queue = Queue()
# 		# Use thread to speed up processing (multithreading)
# 		temp_thread = threading.Thread(None, target=make_sample,
# 		                               name=("1: " + str(mSamp)),
# 		                               args=[adj, temp_queue],
# 		                               daemon=True, )
# 		temp_thread.start()
# 		temp_thread.join()
# 		data_node = temp_queue.get()  # the resulting (samples,thread_time)
# 		if mSamp > 1:
# 			thread_samples(mSamp - 1)
# 		else:
# 			if queue.empty():
# 				data_lst = [data_node]
# 				length = len(data_lst)
# 				print("EMPTY list now ", length, " long")
# 				queue.put(data_lst)
# 			else:
# 				data_lst = queue.get()
# 				data_lst.append(data_node)
# 				length = len(data_lst)
# 				print("list now ", length, " long")
# 				queue.put(data_lst)
#
# 	thread_samples(max_samp)
# 	ret = queue.get()
# 	# print("FINAL LIST IS NOW ", len(ret), "LONG")
# 	queue.put(ret)
# 	return ret


# from strawberryfields.apps import data, sample, subgraph, plot
# import plotly
# import networkx as nx
# import networkx.convert_matrix
# import networkx.classes.graph
# import random
# import networkx.algorithms.operators.binary as bin
# from networkx.generators.random_graphs import erdos_renyi_graph as pGraph
# import numpy as np
# import scipy as sp
# import time
# import queue
# import threading
# import _thread as Thread
# import matplotlib.pyplot as plt
# import array as arr
# import yappi
# from networkx.readwrite.nx_yaml import read_yaml
# import shelve
# import dill
# my_shelf = shelve.open("sample_pregen_dat.out", 'n')
# for key in dir():
#     try:
#         my_shelf[key] = globals()[key]
#     except TypeError:
#         #
#         # __builtins__, my_shelf, and imported modules can not be shelved.
#         #
#         print('ERROR shelving: {0}'.format(key))
# my_shelf.close()
# n_mean = 8
# samples = 5
# t0 = time.time()
# s = sample.sample (adj, n_mean, samples)
# t1 = time.time()
# total_n = t1-t0
# before_post_subgraphs = sample.to_subgraphs(s, graph)
# print(before_post_subgraphs)
# # one of the sampled subgraphs
# before_post_fig = plot.graph(graph, before_post_subgraphs[0])
# before_post_fig.show()
#
# min_clicks = 16
# max_clicks = 30
#
# post = sample.postselect(s, min_clicks, max_clicks)
# post_subgraphs =  sample.to_subgraphs(s, graph)
#
# s.append([0, 1, 0, 1, 1, 0])
# print("Before post select results in nodes: ", len(before_post_subgraphs))
# print(before_post_subgraphs)
# print("After post select results in nodes: ", len(post_subgraphs))
# print(post_subgraphs)
# print("Time: ", total_n)
#
# plt.style.use('seaborn-whitegrid')
# fig = plt.figure()
# ax = plt.axes()


#
# thread = threading(target=classic_gen_time_Sample, name="thread",
#                 args=[20, [], queue], )
#                 args=[20, [], queue], )

# thread_lst.append()
# thread.start()
# thread.join()
# classic_time_sample_data = queue.get()

# plot_graph = plot.graph(graph)
# plot_graph.show()
# 2.2261393070220947 for 5
# original = 69 seconds for 20
