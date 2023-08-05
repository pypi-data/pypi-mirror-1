'''A multithreaded implementation of the papyros master-slave API.'''

__all__ = ['MultiThreadedMaster', 'MultiThreadedSlave']

import logging
import threading
from papyros import Master, Slave

log = logging.getLogger('papyros')


class MultiThreadedMaster(Master):

    def __init__(self, num_slaves, poll_time=1, request_qsize=0, response_qsize=0):
        '''Initialize this master and start C{num_slaves} slaves.

        @param num_slaves: The number of slaves to start initially.
        @param request_qsize: If a positive integer, it's the maximum number
            of unassigned jobs. Trying to L{add <addJob>} a new L{Job}
            when the queue is full blocks or raises C{Queue.Full} exception.
        @param response_qsize: If a positive integer, it's the maximum number
            of completed jobs waiting to be fetched. No more jobs are assigned
            to the slaves when this number is reached.
        '''
        Master.__init__(self, request_qsize, response_qsize)
        for _ in xrange(num_slaves):
            MultiThreadedSlave(self, poll_time).start()
        log.debug('Added %d slave threads' % num_slaves)


class MultiThreadedSlave(Slave, threading.Thread):
    '''A L{Slave} implemented as a daemon thread.'''

    def __init__(self, master, poll_time=1):
        threading.Thread.__init__(self)
        Slave.__init__(self, master, poll_time)
        self.setDaemon(True)
