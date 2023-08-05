import random
from math import sqrt
from os import getpid
from time import sleep, strftime
from threading import currentThread
from itertools import count, ifilter

import papyros


def log(msg):
    print '%s PID=%d/%s:\t%s' % (strftime('%H:%M:%S'), getpid(),
                                  currentThread().getName(), msg)


class SlowSqrt(papyros.Job):
    '''A non-CPU-intensive job: sleep for a few seconds and return the sqrt of
    a number.
    '''

    def __str__(self):
        return 'SlowSqrt(%s)' % self.args[0]

    def __call__(self, n):
        t = random.randrange(1,5)
        log('Pretending to work hard on computing sqrt(%s) for %d seconds' % (n,t))
        sleep(t)
        return sqrt(n)


class PrimeFactors(papyros.Job):
    '''A CPU intensive job: compute the prime factors of a number.'''

    def __str__(self):
        return 'PrimeFactors(%s)' % self.args[0]

    def __call__(self, n):
        log('Factorizing %s' % n)
        factors = []
        nextprime = sieve().next
        candidate = nextprime()
        thresh = sqrt(n)
        while True:
            if candidate > thresh:
                factors.append(n)
                break
            d,m = divmod(n, candidate)
            if m == 0:
                factors.append(candidate)
                n = d; thresh = sqrt(n)
            else:
                candidate = nextprime()
        return factors


def sieve():
    # from Tim Hochberg's comment at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117119
    seq = count(2)
    while True:
        p = seq.next()
        seq = ifilter(p.__rmod__, seq)
        yield p
