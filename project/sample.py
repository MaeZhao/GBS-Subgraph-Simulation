# In this code I will demonstrate the tedious nature of generating your own
# samples

import pickle
import time
import _thread as Thread
import threading
import queue as q

# from multiprocessing_on_dill.queues import Queue
# from multiprocessing_on_dill.pool import Pool
# from multiprocessing_on_dill.managers import Value
# from multiprocessing_on_dill.context import BaseContext

import dill
import networkx as nx
import numpy as np
import multiprocess as mp
from multiprocess import Process, Queue, Pool, Value

from networkx.readwrite.nx_yaml import read_yaml
from strawberryfields.apps import sample

adj = nx.to_numpy_array(read_yaml('union_graph.yaml'))
threads = []
graph = nx.Graph(adj)


def make_sample(f_adj, max_samp, queue):
	start_sampling.wait()
	ts = time.time()
	sampling = sample.sample(f_adj, 8, max_samp)
	start_sampling.set()
	tsf = time.time()
	total_n = ts - tsf
	ret = (total_n, sampling)
	queue.put(ret)
	# time.sleep(0.01)  # kills the thread above
	return ret


def classic_gen_time_Sample1(max_samp, queue):
	def thread_samples(adj, mSamp):
		if (mSamp <= 1):
			lst = []
			temp_que = Queue()
			# Use thread to speed up processing (multithreading)
			temp_thread = threading.Thread(None, target=make_sample,
			                               name=("1: " + str(mSamp)),
			                               args=[adj, mSamp, temp_que],
			                               daemon=True, )
			# temp_thread = threading.Thread(None, target=make_sample,  name=("2:" +
			#                                                                 str(
			# 	                                                                max_Sample)),
			#                                args=[adj, max_Sample, queue], )
			temp_thread.start()
			temp_thread.join()
			time_samp_node = temp_que.get()  # the resulting (samples,thread_time)
			temp_que.task_done()
			lst.append(time_samp_node)
			return (lst, True)
		else:
			rec_val = thread_samples(adj, mSamp - 1)
			temp_que = Queue()
			# Use thread to speed up processing (multithreading)
			temp_thread = threading.Thread(None, target=make_sample,
			                               name=("1: " + str(mSamp)),
			                               args=[adj, mSamp, temp_que],
			                               daemon=True, )
			# temp_thread = threading.Thread(None, target=make_sample,  name=("2:" +
			#                                                                 str(
			# 	                                                                max_Sample)),
			#                                args=[adj, max_Sample, queue], )
			temp_thread.start()
			temp_thread.join()
			time_samp_node = temp_que.get()  # the resulting (samples,thread_time)
			temp_que.task_done()
			# s = queue.get()
			# Use thread to speed up processing (multithreading)
			if (rec_val[1]):
				rec_lst = rec_val[0]
				rec_lst.append(time_samp_node)
				ret = (rec_lst, True)
				# Return the begining of a (time x sample) x boolean tuple list
				return ret
	
	res = thread_samples(adj, max_samp)
	ret = res[0]
	queue.put(ret)
	return ret


# theoretically this is supposed to be slower
def classic_gen_time_Sample2(max_Samp, sample_time_lst, queue):
	if max_Samp <= 0:
		queue.put(sample_time_lst)
		return sample_time_lst
	else:
		temp_que = Queue()
		# Use thread to speed up processing (multithreading)
		temp_thread = threading.Thread(None, target=make_sample,
		                               name=("2: " + str(max_Samp)),
		                               args=[adj, max_Samp, temp_que],
		                               daemon=True, )
		
		temp_thread.start()
		s = temp_que.get()  # the resulting (samples,thread_time)
		temp_thread.join()
		# s = queue.get()
		total_n = s[0]
		print("2", total_n, max_Samp)
		sample_time_lst.append((total_n, max_Samp))
		ret = classic_gen_time_Sample2(max_Samp - 1, sample_time_lst, queue)
		queue.put(ret)
		return ret


def process_thread_1():
	global total_t1
	global classic_time_sample_data1
	# Use thread to speed up processing (multithreading)
	classic_time_sample_data1 = queue1.get()
	# thread1.join()
	tf = time.time()
	total_t1 = tf - t0
	return


def process_thread_2():
	global total_t2
	global classic_time_sample_data2
	# Use thread to speed up processing (multithreading)
	classic_time_sample_data2 = queue2.get()
	# thread2.join()
	tf = time.time()
	total_t2 = tf - t0
	return


# Use thread to speed up processing (multithreading)
# thread1 = threading.Thread(None, target=classic_gen_time_Sample1,
#                            name="1",
#                            args=[5, queue1],
#                            daemon=True, )


# Use thread to speed up processing (multithreading)
# thread2 = threading.Thread(None, target=classic_gen_time_Sample2,
#                            name="2",
#                            args=[5, [], queue2],
#                            daemon=True, )
# queue1 = _Queue.Queue(0)
# queue2 = _Queue.Queue(0)


if __name__ == '__main__':
	mp.set_start_method('spawn')
	start_sampling = threading.Event()
	queue2 = Queue()
	queue1 = Queue()
	maxSample = Value('d', 2.0)
	
	p1 = Process(target=process_thread_1, name="p1", args=(maxSample,))
	# thread1 = threading.Thread(None, target=classic_gen_time_Sample1,
	#                            name="1",
	#                            args=[maxSample, queue1],
	#                            daemon=True, )
	p2 = Process(target=process_thread_2, name="p2", args=(maxSample,))
	# thread2 = threading.Thread(None, target=classic_gen_time_Sample2,
	#                            name="2",
	#                            args=[maxSample, [], queue2],
	#                            daemon=True, )
	# pool = Pool(1)
	# p1 = functools.partial(process_thread_1, )
	# p2 = functools.partial(process_thread_2, )
	
	print("running")
	
	
	# thread1 is parallel to with thread2
	
	def runInParallel(*proc):
		for p in proc:
			p.start()
			p.join()
		return
	
	
	# thread1.start()
	# thread1.join()
	
	# thread2.start()
	# thread1.join()
	
	pool = Pool()
	parallel_run = pool.imap(runInParallel, [p1, p2])
	pool.close()
	pool.join()
	
	print("done with parallel")
	print("data loaded")

# def runInParallel(*funcs):
# 	proc = []
# 	for fn in funcs:
# 		p = Process(target=fn[0], args=fn[1])
# 		p.start()
# 		proc.append(p)
# 	for p in proc:
# 		p.join()
# dill.dump_session("sample_pregen_dat.out")
t0 = time.time()

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
