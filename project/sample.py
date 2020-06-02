# In this code I will demonstrate the tedious nature of generating your own
# samples

import pickle
import time
import warnings
import _thread as Thread
from multiprocessing import Queue, Process, Pool
import random
import functools
import operator
from strawberryfields.apps import data, sample, subgraph, plot

# from multiprocessing_on_dill.queues import Queue
# from multiprocessing_on_dill.pool import Pool
# from multiprocessing_on_dill.managers import Value
# from multiprocessing_on_dill.context import BaseContext
import dill
import networkx as nx
import numpy as np
import multiprocessing as mp
import threading as threading
from networkx.readwrite.nx_yaml import read_yaml
from strawberryfields.apps import sample


def make_sample(f_adj, queue):
	# graph = nx.Graph(f_adj)
	try:
		sampling = sample.sample(f_adj, 8, 5, threshold=True)
		if not sampling:
			make_sample(f_adj, queue)
			return
		else:
			queue.put(sampling)
			return
	except RuntimeWarning:
		print("ERROR RESAMPLE")
		make_sample(f_adj, queue)
		return


def remove_empty(lst):
	try:
		ret = lst.remove([])
		return remove_empty(ret)
	except ValueError:
		return lst


def process_sample(adj, num, temp_queue):
	print("Starting to process sample  ", num)
	# Use thread to speed up processing (multithreading)
	make_sample(adj, temp_queue)
	print("sample ", num, " made")
	# data_nodes = temp_queue.get()  # the resulting (samples,thread_time)
	# temp_queue.put(data_nodes)
	# # if queue.empty():
	# data_lst = data_nodes
	# length = len(data_lst)
	# print("EMPTY list now ", length, " long")
	# queue.put(data_lst)
	return


def process_sample_pool(adj, num):
	print("Starting to process sample  ", num)
	temp_queue = Queue()
	# Use thread to speed up processing (multithreading)
	make_sample(adj, temp_queue)
	print("sample ", num, " made")
	data_nodes = temp_queue.get()  # the resulting (samples,thread_time)
	# temp_queue.put(data_nodes)
	# # if queue.empty():
	# data_lst = data_nodes
	# length = len(data_lst)
	# print("EMPTY list now ", length, " long")
	# queue.put(data_lst)
	return data_nodes


if __name__ == '__main__':
	g_adj = nx.to_numpy_array(read_yaml('union_graph.yaml'))
	
	
	def foldl(func, acc, xs):
		return functools.reduce(func, xs, acc)
	
	
	def compile_result(result):
		global save_pool
		save_pool.extend(result)
	
	
	graph = nx.Graph(g_adj)
	maxSample = 20
	manager = mp.Manager()
	
	iter = int(maxSample / 5)
	
	# t_pool = time.time()
	# pool = mp.Pool(mp.cpu_count())
	# save_pool = manager.list()
	# for i in range(iter):
	# 	queue1 = Queue()
	# 	# t = mp.Value(i, 'i')
	# 	print("starting pool ", (i + 1), " of ", iter)
	# 	print(queue1.empty())
	# 	pool.apply_async(process_sample_pool, args=(g_adj, (i + 1),),
	# 	                 callback=compile_result)
	# pool.close()
	# pool.join()
	# save_pool = sample.to_subgraphs(save_pool, graph)
	# time_pool = time.time() - t_pool
	# print("FINAL pool MATRIX: ", save_pool)
	
	t_p = time.time()
	save = manager.list()
	for i in range(iter):
		queue2 = Queue()
		print(queue2.empty())
		print("starting process ", (i + 1), " of ", iter)
		p = Process(target=process_sample, args=(g_adj, (i + 1), queue2,))
		p.start()
		p.join()
		v = queue2.get()
		# v = sample.postselect(v, 3, 30)
		print("left process ", (i + 1), "of", iter)
		save.extend(v)
	
	print(queue2.empty())
	save = sample.to_subgraphs(save, graph)
	total_time_process = time.time() - t_p
	print("FINAL MATRIX LENGTH: ", save)
	
	# Debug
	print("PROCESS TIME: ", total_time_process)
	# print("POOL TIME: ", time_pool)
	
	filename = 'SAVE-DATA3.pkl'
	print("saving to ", filename)
	outfile = open(filename, 'wb')
	pickle.dump(save, outfile)
	outfile.close()
	print("done with parallel")
	print("data loaded")

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

# OLD CODE:
# ___________________________________________________________________________


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
