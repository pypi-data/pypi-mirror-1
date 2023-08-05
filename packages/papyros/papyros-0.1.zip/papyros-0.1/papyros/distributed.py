#!/usr/bin/env python

'''A multiprocess implementation of the papyros master-slave API.

Both the master and the slaves run as separate processes on one or more machines.
This module is also executable, spawning the master or slave processes. Run as::

    python -m papyros.distributed --help

to see the list of available options.

@requires: U{Pyro <http://pyro.sourceforge.net/>}.
'''


__all__ = ['DistributedMaster', 'DistributedSlave', 'DEFAULT_GROUP']

import os
import sys
import logging
from time import sleep
from subprocess import Popen
from optparse import OptionParser, make_option

from Pyro.core import ObjBase
from Pyro.configuration import Config
from Pyro.errors import NamingError, ConnectionClosedError

from papyros import Master, Slave, enableLogging
from papyros.simplepyro import publish_object, get_proxy, serve_forever


DEFAULT_GROUP = ':Papyros'
log = logging.getLogger('papyros')


class DistributedMaster(ObjBase, Master):

    def __new__(cls, group_name=DEFAULT_GROUP, *args, **kwds):
        try: return get_proxy(cls.name(group_name))##, with_attrs=True)
        except NamingError, ex:
            return super(DistributedMaster,cls).__new__(cls, group_name,
                                                        *args, **kwds)

    def __init__(self, group_name=DEFAULT_GROUP, *args, **kwds):
        ObjBase.__init__(self)
        Master.__init__(self, *args, **kwds)
        publish_object(self, self.name(group_name))

    @classmethod
    def name(cls, group_name):
        return group_name + '.Master'


class DistributedSlave(ObjBase, Slave):

    def __init__(self, group_name=DEFAULT_GROUP, poll_time=1):
        ObjBase.__init__(self)
        Slave.__init__(self, None, poll_time)
        self._master_name = DistributedMaster.name(group_name)

    def run(self):
        while True:
            if self._master is None:
                try:
                    self._master = get_proxy(self._master_name)
                    log.info('Connected to master: %s' % self._master.URI)
                except NamingError,ex:
                    sleep(3); continue
            try: self.process()
            except ConnectionClosedError:
                log.warn('Disconnected from master')
                self._master = None


if __name__ == '__main__':
    parser = OptionParser(
        description = "To start a master process, don't specify the --slave/-s option. "
                      "To start N slave processes on this host, give --slave=N.",
        option_list = [
            make_option('-s', '--slaves', type='int',
                        help='Number of new slaves to spawn'),
            make_option('-g', '--group', default=DEFAULT_GROUP,
                        help='Name of the Pyro process group'),
            make_option('-c', '--config', metavar='FILE', default='',
                        help='Pyro configuration file'),
            make_option('-l', '--logging', action='store_true',
                        help='Print out logging messages'),
    ])
    options = parser.parse_args()[0]
    if options.logging:
        enableLogging()
    if options.config:
        config = Config()
        config.setup(options.config)
    if not options.slaves:
        master = DistributedMaster(options.group)
        try: uri = master.URI
        except AttributeError:
            uri = master.getProxy().URI
            print 'Starting master of group "%s" at %s' % (options.group,uri)
            serve_forever(disconnect=True)
        else:
            print 'Master of group "%s" is already started and listening at %s!' % (
                options.group, uri)
    else:
        if options.slaves > 1:
            cmd = ['python', '-m', 'papyros.distributed', '--slaves=1',
                   '--group=%s' % options.group]
            if options.config:
                cmd.append('--config=%s' % options.config)
            if options.logging:
                cmd.append('--logging')
            for n in xrange(options.slaves-1):
                Popen(cmd)
        print 'Starting slave process (PID=%s)' % os.getpid()
        DistributedSlave(options.group).run()
