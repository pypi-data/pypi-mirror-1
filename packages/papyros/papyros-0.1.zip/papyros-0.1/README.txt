Papyros: Lightweight master-slave parallel processing in Python
===============================================================

**Papyros** is a small platform independent parallel processing Python package, providing a master-slave model. Clients can submit jobs to a master object which is monitored by one or more slave objects that do the real work and return the processed jobs back to the master. Two main implementations are currently provided, one using multiple threads and one multiple processes in one or more hosts (through Pyro_). The primary design goal is simplicity: a user can replace a time consuming loop in a single-threaded single-process program with the equivalent parallel version in a few lines of code, with minimal boilerplate overhead.

Bug reports, feature requests and patches are welcome_. No promises though; I can't tell how often or for how long I will actively maintain the project, so people interested in participating may `contact me`_ as well.

*George Sakkis*


Installation
------------
Installation uses the standard distutils command; just run from the distibution's directory::

    python setup.py install

Papyros has been (lightly) tested on Windows XP (Python 2.5, Pyro 3.7) and Linux (Python 2.4/2.5, Pyro 3.7). Pyro is required only for the distributed implementation; the single-process implementations don't need it.

Usage
-----
The typical steps for using Papyros are outlined below. For more details consult the documentation_.

1. Create the job type(s)
~~~~~~~~~~~~~~~~~~~~~~~~~
Each type of task to be processed concurrently must extend the callable ``papyros.Job`` class and override its ``__call__`` method. Any number of positional and named arguments are allowed. A prime factorization job can simply be::

    import papyros

    class Factorization(papyros.Job):
        '''A job for factorizing a single number.'''

        def __call__(self, num):
            # <-- find the prime factors here --> #
            return primes

2. Create a ``Master`` object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The master object implements the ``papyros.Master`` interface. Currently two main implementations are provided, a multithreaded and a distributed one [1]_:

- **Multithreaded mode**
  ::

    from papyros.multithreaded import MultiThreadedMaster
    # create a master with 3 slave threads
    master = MultiThreadedMaster(3)

- **Distributed mode**

  There are four steps to use Papyros in distributed mode. These steps don't have to be taken on the same host; in fact each of them may be run on a separate machine. This mode requires Pyro_ to be installed on all participating hosts [2]_.

  1. Start the Pyro name server::

      pyro-ns

  2. Start the master process::

      python -m papyros.distributed [--logging] [--group=process_group] [--config=Pyro_config_file]

     ``process_group`` is an optional name identifying the master-slave group (by default ``papyros.distributed.DEFAULT_GROUP``)

  3. Start one or (typically) more slave processes on one or more machines::

      python -m papyros.distributed --slaves=3 [--logging] [--group=process_group] [--config=Pyro_config_file]

     This starts 3 slaves processes on the machine it was issued. Repeat this for every machine in the group.

  4. Create the master object in the client::

      from papyros.distributed import DistributedMaster
      master = DistributedMaster(process_group)

     As in the previous steps, the ``process_group`` is optional. If specified, it must be the same in all steps.

  Steps (2) and (3) are actually independent. The slave processes may be started before the master and they will connect automatically to their master once it starts.

3. Submit a number of jobs to the master
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Given a master object, the client can add any number of jobs to be processed. Each job is created by passing the arguments that are expected by its ``__call__``::

    # compute the primes factors of 10 random numbers
    import random
    for _ in xrange(10):
        master.addJob(Factorization(random.randrange(1e6,1e7)))

Of course it's not mandatory to add all the jobs upfront but that's a common approach.

4. Receive the processed jobs from the master
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once one or more jobs are submitted, the client can ask from the master the next available processed job by calling ``popProcessedJob``::

   # blocks until a job has finished and returns it
   job1 = master.popProcessedJob()
   # non-blocking call; returns a processed job if there is one available immmediately, or None otherwise
   job2 = master.popProcessedJob(timeout=0)
   # blocks no more than 2.5 seconds; returns None if there's no available job after the deadline
   job3 = master.popProcessedJob(timeout=2.5)

``popProcessedJob`` returns either None or one of the previously submitted jobs. In the latter case, the processed job encapsulates the result of the job or the raised exception::

    try: print 'Job %s returned %r' % job.result
    except Exception, ex:
        print 'Job %s raised an exception: ' % ex
        # the original traceback printout is also available through the traceback attribute
        print 'Original traceback\n%s' % ex.traceback

A handy idiom to loop over the processed jobs is by using the ``iter`` builtin in its less known form ``iter(callable, sentinel)``::

    # loop over all pending jobs
    for job in iter(master.popProcessedJob, None):
        print job.result
    # loop over pending jobs as long each job is available within 2 seconds from the previous one
    for job in iter(lambda: master.popProcessedJob(timeout=2), None):
        print job.result

From the last example it can be inferred that if there are 30 pending jobs, the whole loop will take at most 1 minute; for 60 jobs it would be at most 2 minutes, etc. For cases where there has to be an upper limit for the loop independently of the number of jobs, the ``processedJobs`` method comes in handy::

    # returns a list of jobs available within 10 seconds
    jobs = master.processedJobs(timeout=10)
    print '%s jobs finished' % len(jobs)

Examples
--------
The ``examples/demo.py`` script illustrates the Papyros API and its three implementations (singlethreaded, multithreaded, distributed). There are two sample job types, a cpu-intensive (``PrimeFactors``) and a non-cpu-intensive (``SlowSqrt``). The demo also show the ``cancelAllJobs`` method that discards all currently unassigned jobs (it has no effect on jobs already assigned to a slave).

To run the demo, just give ``python examples/demo.py`` and answer the questions when prompted. Note for that for the distributed version, both the master and the slave processes should be able to import ``papyros`` and the ``jobs.py`` module under the ``examples`` directory.


Notes
~~~~~
.. [1] There is also a third, non-concurrent version, mainly for the sake of completeness and as a fallback in systems where the concurrent versions are not available.
.. [2] The module(s) required by the job types to be processed must also be importable from all hosts. In a future version this restriction may be raised by enabling the PYRO_MOBILE_CODE feature.

.. _Pyro: http://pyro.sourceforge.net/
.. _welcome:  http://code.google.com/p/papyros/issues/list
.. _`contact me`: mailto:george.sakkis@gmail.com
.. _documentation: docs/index.html
