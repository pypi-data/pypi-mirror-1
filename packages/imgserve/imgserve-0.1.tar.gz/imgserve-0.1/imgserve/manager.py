"""
Manages the http server process and worker processes and communication
among them.
"""

import sys
import time
import os
import signal
import Queue
import asyncore
import threading
from multiprocessing import Process, cpu_count, JoinableQueue
from imgserve.http import httpserv
from imgserve.worker import work


class ImgManager:
    """
    This manager starts the http server processes and worker
    processes, creates the input/output queues that keep the processes
    work together nicely.
    """
    def __init__(self):
        self.NUMBER_OF_PROCESSES = cpu_count()

    def start(self, host, port):
        self.i_queue = JoinableQueue()
        self.o_queue = JoinableQueue()

        # Create worker processes
        print "Starting %s worker process(es)" % self.NUMBER_OF_PROCESSES
        self.workers = [Process(target=work,
                                name="imgserve: worker process %s" % str(i+1),
                                args=(self.i_queue, self.o_queue))
                        for i in range(self.NUMBER_OF_PROCESSES)]
        for w in self.workers:
            w.start()

        # Create the http server process
        print "Starting HTTP process"
        self.http = Process(target=httpserv, args=(host, port,
                                                   self.i_queue, self.o_queue))
        self.name = "imgserve: http server"
        self.http.start()

        # Keep the current process from returning
        self.running = True
        while self.running:
            time.sleep(1)
        self.http.join()

    def stop(self):
        print "imgserve shutting down"

        # Stop accepting new requests from users
        os.kill(self.http.pid, signal.SIGINT)

        # Waiting for all requests in output queue to be delivered

        # Tired of http://bugs.python.org/issue4660 issue, a dirty
        # hack
        while True:
            try:
                self.o_queue.task_done()
            except ValueError:
                break
        self.o_queue.join()

        # Put sentinel None to input queue to signal worker processes
        # to terminate
        self.i_queue.put(None)
        for w in self.workers:
            w.join()

        # There is one last None left in i_queue
        assert self.i_queue.get() is None
        assert self.i_queue.qsize() is 0

        # Tired of http://bugs.python.org/issue4660 issue, a dirty
        # hack
        while True:
            try:
                self.i_queue.task_done()
            except ValueError:
                break
        self.i_queue.join()
        self.running = False

    def kill(self):
        """Stop violently."""
        self.http.terminate()
        for w in self.workers:
            w.terminate()
            print "Terminate worker process"
        self.running = False
        print "Change self.running to False"
