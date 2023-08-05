'''A non-concurrent implementation of the papyros master-slave API.

This is mainly for the sake of completeness and perhaps as a fallback in systems
that the concurrent implementations are not available.
'''

__all__ = ['SingleThreadedMaster']

from papyros import Master, Slave

class SingleThreadedMaster(Master,Slave):

    def __init__(self, poll_time=1, request_qsize=0, response_qsize=0):
        Master.__init__(self, request_qsize, response_qsize)
        Slave.__init__(self, self, poll_time)

    def popProcessedJob(self, timeout=None):
        if timeout > 0:
            raise ValueError('Cannot guarantee non-zero timeout in single-threaded mode')
        if timeout is None:
            self.process()
        return Master.popProcessedJob(self,timeout)
