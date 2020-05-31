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


# theoretically this is supposed to be faster
def classic_gen_time_Sample1(max_Sample, queue):
	def thread_samples(adj, max_Sample):
		if (max_Sample <= 1):
			lst = []
			temp_que = _Queue.Queue()
			# Use thread to speed up processing (multithreading)
			temp_thread = threading.Thread(None, target=make_sample,
			                               name=("2: " + str(max_Sample)),
			                               args=[adj, max_Sample, temp_que],
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
			rec_val = thread_samples(adj, max_Sample - 1)
			temp_que = _Queue.Queue()
			# Use thread to speed up processing (multithreading)
			temp_thread = threading.Thread(None, target=make_sample,
			                               name=("2: " + str(max_Sample)),
			                               args=[adj, max_Sample, temp_que],
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
	
	res = thread_samples(adj, max_Sample)
	ret = res[0]
	queue.put(ret)
	return ret


ti1 = time.time()
# Samples all 20 subgraphs
# classic_time_sample_data = classic_gen_time_Sample1(2, [])
queue1 = _Queue.Queue()
# Use thread to speed up processing (multithreading)
thread1 = threading.Thread(None, target=classic_gen_time_Sample1,
                           name="1",
                           args=[5, queue1],
                           daemon=True, )
thread1.start()
# time.sleep(0.01)  # kills the thread above
thread1.join()
tf1 = time.time()
final_time1 = tf1 - ti1  # Total time after sampling all subgraphs
classic_time_sample_data = queue1.get()
print(classic_time_sample_data)

# Saving our time x sample size data:
dill.dump_session("sample_thread_TxS.pkl")
# np.save('sample_thread_TxS.npy', classic_time_sample_data)
# # Saving our entire session for debugging:
# my_shelf = shelve.open("sample_thread.pkl", 'n')
# for key in dir():
# 	try:
# 		my_shelf[key] = globals()[key]
# 	except TypeError:
# 		#
# 		# __builtins__, my_shelf, and imported modules can not be shelved.
# 		#
# 		print('ERROR shelving: {0}'.format(key))
# my_shelf.close()

# np.save('sample_thread_TxS.npy', classic_time_sample_data)
# # Saving our entire session for debugging:
# my_shelf = shelve.open("sample_thread.out", 'n')
# for key in dir():
# 	try:
# 		my_shelf[key] = globals()[key]
# 	except TypeError:
# 		#
# 		# __builtins__, my_shelf, and imported modules can not be shelved.
# 		#
# 		print('ERROR shelving: {0}'.format(key))
# my_shelf.close()

# Load
# my_shelf = shelve.open('sample_thread_TxS.npy')
# for key in my_shelf:
#     globals()[key]=my_shelf[key]
# my_shelf.close()

# Saving our time x sample size data:
# np.save('sample_timeXsize.npy', classic_time_sample_data)
# Saving our entire session for debugging:
# save = globals()

# for key in save:
# 	try:
# 		n_val = save[key]
# 		n_pair = {key: n_val}
# 		dill.dump("sample_pregen_dat.pkl", n_pair)
#
# 	except TypeError:
# 		#
# 		# __builtins__, my_shelf, and imported modules can not be shelved.
# 		#
# 		print('ERROR shelving: {0}'.format(key))

# dill.dump_session("sample_pregen_dat.pkl")
# To load data:
# dill.load_session("sample_pregen_dat.out")
# import gzip
# gz = gzip.open("sample_pregen_dat" + '.gz', 'rb')
# obj = pickle.loads(gz.read())
# gz.close()
