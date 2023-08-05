'''Reduces the Pyro boilerplate code for several common functions.'''

__all__ = ['DAEMON', 'NAME_SERVER', 'create_proxy', 'get_proxy']

import sys
from Pyro.errors import PyroError
from Pyro.protocol import getHostname
from Pyro.naming import NameServerLocator, NameServerProxy
from Pyro.core import Daemon, PyroURI, ObjBase, DynamicProxy, DynamicProxyWithAttrs

DAEMON = None
NAME_SERVER = None


def locate_nameserver(host=None, port=None):
    global NAME_SERVER
    if NAME_SERVER is not None and host is None:
        return NAME_SERVER
    NAME_SERVER = None
    if host is not None:
        try: NAME_SERVER = NameServerProxy(PyroURI(host))
        except PyroError: pass
    if NAME_SERVER is None:
        NAME_SERVER = NameServerLocator().getNS(host=host, port=port)
    ##print 'Naming Service found at', NAME_SERVER.URI
    return NAME_SERVER

def init_daemon(host=None, port=None):
    global DAEMON
    if DAEMON is None:
        DAEMON = Daemon(host=host, port=port)

def publish_object(obj, name=None, host=None, port=None,
                   nameserver_host=None, nameserver_port=None):
    init_daemon(host,port)
    if name is not None:
        DAEMON.useNameServer(locate_nameserver(nameserver_host, nameserver_port))
        parts = name.split('.')[:-1]
        if parts:
            group = parts.pop(0)
            while True:
                ##print 'Creating group', group
                try: NAME_SERVER.createGroup(group)
                except PyroError, ex: pass ##print ex
                if not parts:
                    break
                group += '.%s' % parts.pop(0)
        # unregister previous object with this name (if any)
        try: NAME_SERVER.resolve(name)
        except PyroError, ex: pass ##print "!!", type(ex), ex
        else: NAME_SERVER.unregister(name)
    if not isinstance(obj, ObjBase):
        temp = ObjBase()
        temp.delegateTo(obj)
        obj = temp; del temp
    ##print 'creating', name
    return DAEMON.connect(obj, name)

def get_proxy(name, with_attrs=False, nameserver_host=None, nameserver_port=None):
    name_server = locate_nameserver(nameserver_host,nameserver_port)
    proxy_cls = with_attrs and DynamicProxyWithAttrs or DynamicProxy
    return proxy_cls(name_server.resolve(name))

def serve_forever(disconnect=False, host=None, port=None):
    init_daemon(host,port)
    print >> sys.stderr, 'Waiting for connections at %s:%s ..' % (DAEMON.hostname,
                                                                  DAEMON.port)
    try: DAEMON.requestLoop()
    finally: DAEMON.shutdown(disconnect=disconnect)
