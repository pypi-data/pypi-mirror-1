'''A small platform independent parallel processing package.

This package provides a master-slave parallel processing model in Python.
Clients can submit jobs to a L{Master} object which is monitored by one or more
L{Slave} objects that do the real work and return the processed L{Job}s back to
the master. Two main implementations are currently provided, one L{multithreaded}
and one L{distributed} in one or more hosts (through U{Pyro <http://pyro.sourceforge.net/>}).
'''

__all__ = ['Master', 'Slave', 'Job', 'UnprocessedJobError']

import os
import sys
import Queue
import logging, logging.config
from cStringIO import StringIO
from traceback import print_exception

log = logging.getLogger('papyros')

def enableLogging():
    logging.config.fileConfig(os.path.join(os.path.dirname(__file__),
                                               'logging.conf'))

def synchronized(f):
    '''A synchronized method decorator'''
    return f
    def wrapper(self, *args, **kwargs):
        try: lock = self.__lock
        except AttributeError: # first time use
            lock = self.__dict__.setdefault('__lock', RLock())
        lock.acquire()
        try: return f(self, *args, **kwargs)
        finally: lock.release()
    return wrapper


class Master(object):
    'A L{Job} dispatcher object, controlling a set of L{slaves <Slave>}.'

    def __init__(self, input_size=0, output_size=0):
        '''Initialize this master.

        @param input_size: If a positive integer, it's the maximum number
            of unassigned jobs. Trying to L{add <addJob>} a new L{Job}
            when the queue is full blocks or raises C{Queue.Full} exception.
        @param output_size: If a positive integer, it's the maximum number
            of completed jobs waiting to be fetched. No more jobs are assigned
            to the slaves when this number is reached.
        '''
        self._inProgressJobs = set()
        self._unassignedJobs = Queue.Queue(input_size)
        self._processedJobs = Queue.Queue(output_size)

    def addJob(self, job, timeout=None):
        '''Add a L{Job} to the input queue.

        @param timeout: If the input queue is full and C{timeout is None}, block
            until a slot becomes available. If C{timeout > 0}, block for up to
            C{timeout} seconds and raise C{Queue.Full} exception if the queue is
            still full. If C{timeout <= 0}, do not block and raise C{Queue.Full}
            immediately if the queue is full.
        '''
        self._unassignedJobs.put(job, timeout is None or timeout>0, timeout)
        log.debug('Pushed job %s to the input queue' % job)

    def cancelAllJobs(self):
        '''Cancel all unassigned jobs.'''
        while True:
            try: job = self._unassignedJobs.get(timeout=0)
            except Queue.Empty: break
            log.debug('Cancelled job %s' % job)

    def numPendingJobs(self):
        'Return the approximate number of pending (waiting or in progress) jobs.'
        return self._unassignedJobs.qsize() + len(self._inProgressJobs)

    def popProcessedJob(self, timeout=None):
        '''Pop the next processed L{Job} from the output queue.

        If there are no pending jobs, it returns C{None}. Otherwise:
            - If C{timeout is None}, block until a job has finished and return it.
            - If C{timeout <= 0}, return the first finished job that is
                immediately available without blocking, or C{None} otherwise.
            - If C{timeout > 0}, wait up to C{timeout} seconds for a job to
                finish and return it; return C{None} if no job has finished by
                the deadline.

        @returns: The next processed L{Job} or C{None} if there is no available
            for the given C{timeout}.
        '''
        if not self.numPendingJobs():
            return None
        block = timeout is None or timeout>0
        try: job = self._processedJobs.get(block, timeout)
        except Queue.Empty:
            return None
        log.debug('Popped job %s from the output queue' % job)
        assert job is not None
        self._inProgressJobs.remove(job)
        return job

    def processedJobs(self, timeout=None):
        '''Return a list of processed jobs.

        @param timeout: If C{timeout is None} or C{timeout <= 0}, it is
            equivalent to keep calling L{popProcessedJob} until it returns None.
            If C{timeout > 0}, this is the maximum overall time to spend on
            collecting processed jobs.
        '''
        if timeout is None or timeout <= 0:
            return list(iter(lambda: self.popProcessedJob(timeout), None))
        from time import time
        end = time() + timeout
        processed = []
        while timeout > 0:
            job = self.popProcessedJob(timeout)
            if job is None:
                break
            processed.append(job)
            timeout = end - time()
        return processed

    def _assignJob(self, poll_time=10):
        '''Pop the next unassigned non-cancelled job.

        If there are no assigned jobs, keep polling every C{poll_time} seconds
        until one comes in. If the job has been cancelled, it is silently
        discarded. This method should only be called by a L{Slave} of this master.
        '''
        while True:
            # blocks here for poll_time seconds if there are no assigned jobs
            try: job = self._unassignedJobs.get(timeout=poll_time)
            except Queue.Empty:
                return None
            log.debug('Popped job %s from the input queue' % job)
            self._inProgressJobs.add(job)
            return job

    def _getProcessedJob(self, job):
        '''Add a processed job in the output queue.

        This method should only be called by a L{Slave} of this master.
        '''
        # blocks here if outputQueue is full
        self._processedJobs.put(job)
        log.debug('Pushed job %s to the output queue' % job)


class Slave(object):
    '''Abstract Slave class.

    A L{Slave} sits in a loop waiting for L{Job}s from its L{Master}, picks the
    next available job, processes it, sends it back to the L{Master} and all
    over again.
    '''
    def __init__(self, master, poll_time=1):
        '''
        @param master: The L{Master} this slaves is communicating with.
        @param poll_time: How often should this slave poll its master for a new
            L{Job}.
        '''
        if poll_time <= 0:
            raise ValueError('Poll time must be positive')
        self._master = master
        self._pollTime = poll_time

    def run(self):
        while True:
            self.process()

    def process(self):
        '''Fetch the next available unassigned job from the master, process it
        and send it back.

        @returns: The processed job, or None if no job was assigned within
            C{poll_time} seconds.
        '''
        job = self._master._assignJob(self._pollTime)
        if job is not None:
            job._process()
            self._master._getProcessedJob(job)
            log.debug('Finished job %s' % job)
        return job


class Job(object):
    '''Abstract base class of a callable to be called later.

    It stores the result or raised exception of the last time it is called.
    '''
    __counter = 0

    @synchronized
    def __init__(self, *args, **kwds):
        self.args = args
        self.kwds = kwds
        self.__exception = None
        Job.__counter += 1
        self.__id = Job.__counter

    def __hash__(self):
        return self.__id

    def __eq__(self, other):
        try: return self.__id == other.__id
        except AttributeError: return False

    def __call__(self, *args, **kwds):
        '''Abstract method; to be implemented by subclasses.'''
        raise NotImplementedError('Abstract method')

    @property
    def result(self):
        '''Return the computed result for this processed job.

        If the callable had risen an exception, it is reraised here. The original
        traceback is also available as C{exc.__traceback__}.

        If this job has not been processed yet, it raises L{UnprocessedJobError}.
        '''
        if self.__exception is not None:
            raise self.__exception
        try: return self.__result
        except AttributeError:
            raise UnprocessedJobError()

    def _process(self):
        '''Execute this job and store the result or raised exception.

        To be called by L{Slave} instances.
        '''
        log.debug('Ready to process job %s' % self)
        try:
            self.__result = self(*self.args, **self.kwds)
        except Exception, ex:
            type, value, traceback = sys.exc_info()
            out = StringIO()
            # omit the current level of the traceback; start from the next
            print_exception(type, value, traceback.tb_next, file=out)
            # XXX: something like this will be done automatically if PEP 344 is accepted
            ex.traceback = out.getvalue()
            self.__exception = ex
            log.debug('Failed to process job %s' % self)
        else:
            self.__exception = None
            log.debug('Job %s was processed successfully' % self)


class UnprocessedJobError(Exception):
    '''Raised when attempting to get the result of a L{Job} that has not been
    processed yet.
    '''
