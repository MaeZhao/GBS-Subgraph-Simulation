# In this code I will demonstrate the tedious nature of generating your own
# samples
import _thread as Thread
import threading
import queue as _Queue
import time

import dill
import shelve
import networkx as nx
import numpy as np
from networkx.readwrite.nx_yaml import read_yaml
from strawberryfields.apps import sample

adj = nx.to_numpy_array(read_yaml('union_graph.yaml'))
threads = []
graph = nx.Graph(adj)


def make_sample(adj, max_Sample, queue):
	t0 = time.time()
	sampling = sample.sample(adj, 8, max_Sample)
	t1 = time.time()
	total_n = t1 - t0
	ret = (total_n, sampling)
	queue.put(ret)
	# time.sleep(0.01)  # kills the thread above
	return ret


def classic_gen_time_Sample2(max_Samp, sample_time_lst, queue):
	if max_Samp <= 0:
		queue.put(sample_time_lst)
		return sample_time_lst
	else:
		temp_que = mQueue.Queue(0)
		# Use thread to speed up processing (multithreading)
		temp_thread = threading.Thread(None, target=make_sample,
		                               name=("2: " + str(max_Samp)),
		                               args=[adj, max_Samp, temp_que],
		                               daemon=True, )
		
		temp_thread.start()
		s = temp_que.get()  # the resulting (samples,thread_time)
		temp_que.task_done()
		# s = queue.get()
		total_n = s[0]
		print("2", total_n, max_Samp)
		sample_time_lst.append((total_n, max_Samp))
		ret = classic_gen_time_Sample2(max_Samp - 1, sample_time_lst, queue)
		temp_que.put(ret)
		temp_thread.join()
		return ret

ti = time.time()
# Samples all 20 subgraphs
# classic_time_sample_data = classic_gen_time_Sample2(2, [])
queue = _Queue.Queue()
# Use thread to speed up processing (multithreading)
thread = threading.Thread(None, target=classic_gen_time_Sample,
                           name="2",
                           args=[5, [], queue],
                           daemon=True, )
thread.start()
# time.sleep(0.01)  # kills the thread above
thread.join()
tf = time.time()
final_time2 = tf - ti  # Total time after sampling all subgraphs
classic_time_sample_data = queue.get()

# Saving our time x sample size data:
dill.dump_session("/tmp/sample_noThread_TxS.pkl")
# Loading session
# dill.load_session("/tmp/sample_noThread_TxS.pkl")
