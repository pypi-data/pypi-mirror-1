import copy
import functools
import logging
import os
import Queue
import threading
import threadpool
import urlparse



class WorkerThread(threadpool.WorkerThread):
    
    def __init__(self, requests_queue, results_queue, poll_timeout=5, **kwds):
        
        threadpool.WorkerThread.__init__(
            self, requests_queue, results_queue, poll_timeout=poll_timeout, **kwds
        )
        return

    
    def executeEnvironment(self, value=None):
        if value is not None:
            self._executeEnvironment = value
        if not hasattr(self, '_executeEnvironment'):
            self._executeEnvironment = None
        return self._executeEnvironment


    def run(self):
        """
        This is here so that we can override the except clause
        in the super class with the one here
        so that Queue is defined
        """
        # Repeatedly process the job queue until told to exit.
        while True:
            if self._dismissed.isSet():
                # we are dismissed, break out of loop
                break
            # get next work request. If we don't get a new request from the
            # queue after self._poll_timout seconds, we jump to the start of
            # the while loop again, to give the thread a chance to exit.
            try:
                request = self._requests_queue.get(True, self._poll_timeout)
            except Exception, e:
                if Queue is None:
                    # if we hit here
                    # then most likely the program has ended
                    break
                if isinstance(e, Queue.Empty):
                    continue
                raise
            else:
                if self._dismissed.isSet():
                    # we are dismissed, put back request in queue and exit loop
                    self._requests_queue.put(request)
                    break
                    
                self.executeRequest(request)
                pass
            pass
        return
        
        
    def executeRequest(self, request):
        try:
            # we need to keep track of the worker that executed the task
            # so that we can destage files and 
            # and have debugging info
            # This is the line that differentiates this subclass
            # from threadpool.WorkerThread
            request.kwds['worker thread'] = self
                        
            result = request.callable(*request.args, **request.kwds)
            self._results_queue.put((request, result))
        except Exception, e:
            request.exception = True
            import sys
            self._results_queue.put((request, sys.exc_info()))
        return
    

    # END class WorkerThread
    pass


class Pool(threadpool.ThreadPool):

    def isEmpty(self):
        return len(self.workers) is 0
    
    def assignWorker(self):
        # this needs to associate the thread with the virtual machine
        workerThread = WorkerThread(
            self._requests_queue,
            self._results_queue, poll_timeout=5)
        self.workers.append(workerThread)
        return workerThread

    def dismissWorker(self, worker=None, callback=None):
        if not len(self.workers):
            raise ValueError('there are no workers to dismiss')
        
        if worker is None:
            worker = self.workers.pop()

        worker.dismiss()
        worker.join()
        if callback is not None:
            callback(worker)
        return
        
    # END class Pool
    pass


