#!/usr/bin/env python

import sys
import random
from time import sleep

import papyros
import jobs

log = jobs.log


def main():
    # select job type
    j = raw_input('Select job type ([S]lowSqrt, [P]rimeFactors): ')[0].upper()
    if j == 'S':
        job_type = jobs.SlowSqrt
    elif j == 'P':
        job_type = jobs.PrimeFactors

    # select number of jobs
    num_jobs = int(raw_input('Select number of jobs: '))

    # select verbosity
    if raw_input('Verbose output ([Y/N]) ?  ').upper().startswith('Y'):
        papyros.enableLogging()

    # select master type
    m = raw_input('Select master type ([S]inglethreaded, [M]ultithreaded, '
                  '[D]istributed): ')[0].upper()
    if m == 'S':
        from papyros.singlethreaded import SingleThreadedMaster
        master = SingleThreadedMaster()
    elif m == 'M':
        from papyros.multithreaded import MultiThreadedMaster
        num_slaves = int(raw_input('Select number of slave threads: '))
        master = MultiThreadedMaster(num_slaves)
    elif m == 'D':
        from papyros.distributed import DistributedMaster, DEFAULT_GROUP
        group = raw_input('Select distributed group name [default=%s]: ' % DEFAULT_GROUP)
        if not group.strip():
            group = DEFAULT_GROUP
        raw_input('Make sure you have started a master process and one or more '
                  'slave processes for group %r and press any key..' % group)
        master = DistributedMaster(group)
    else:
        sys.exit('Invalid master type')

    # start the demo
    finished_jobs = run(master, job_type, num_jobs)
    for i,job in enumerate(finished_jobs):
        try: out = job.result
        except Exception, ex: out = ex
        print 'Job %2d: (%s)\t%s' % (i, job, out)


def run(master, job_type, num_jobs):
    finished_jobs = []
    def job_done(job):
        finished_jobs.append(job)
        # job.result will reraise any exception raised while the job was being
        # processed; otherwise it will return the computed result
        try: log('job #%s: result=%s' % (job, job.result))
        except Exception, ex:
            log('job #%s: exception raised: %s\n%s' % (job, ex, ex.traceback))

    # create 12 jobs and add them in the queue
    for i in xrange(num_jobs):
        master.addJob(job_type(random.randrange(-sys.maxint,sys.maxint)))

    # collect all processed jobs within 3.5 seconds
    log('** [1] Starting processedJobs with timeout=3.5')
    try: firstbatch = master.processedJobs(timeout=3.5)
    except Exception, ex: log(ex)
    else:
        log('%d jobs done:' % len(firstbatch))
        for job in firstbatch:
            job_done(job)
        log('** [1] finished; %d pending jobs' % master.numPendingJobs())

    # non-blocking iterator over processed jobs
    log('** [2] Starting non-blocking loop')
    for i in xrange(4):
        for job in iter(lambda: master.popProcessedJob(timeout=0), None):
            job_done(job)
        if master.numPendingJobs():
            log('Do something in the main thread; will check again after a sec')
            sleep(1)
    log('** [2] finished; %d pending jobs' % master.numPendingJobs())

    # toss a coin on whether to cancel the remaining jobs
    if random.random() > 0.5:
        master.cancelAllJobs()
        log('Cancelled all remaining unassigned jobs')
    # blocking iterator over any remaining pending jobs
    log('** [3] Starting blocking loop')
    for job in iter(master.popProcessedJob, None):
        job_done(job)
    log('** [3] finished; %d pending jobs' % master.numPendingJobs())
    return finished_jobs


if __name__ == '__main__':
    random.seed()
    main()
