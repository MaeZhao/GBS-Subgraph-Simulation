from multiprocessing import Pool
from os import fork, getpid
import logging

def runs_in_subprocess():
    logging.info(
        "I am the child, with PID {}".format(getpid()))
    
if __name__ == '__main__':
    logging.basicConfig(
        format='GADZOOKS %(message)s', level=logging.DEBUG)
    with Pool() as pool:
        pool.apply(runs_in_subprocess)