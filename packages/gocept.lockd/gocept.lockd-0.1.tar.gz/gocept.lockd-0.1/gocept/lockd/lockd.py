# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import SimpleXMLRPCServer
import os.path
import zc.lockfile


def run_locked(function):
    def wrapped(self, resource, client):
        lock = self._acquire()
        try:
            return function(self, resource, client)
        finally:
            lock.close()
    wrapped.__name__ = function.__name__
    return wrapped


class Lockd(object):

    def __init__(self, lockdir):
        self.lockdir = lockdir
        self.server_lock = os.path.join(self.lockdir, 'lockd.lock')

    def _acquire(self):
        while True:
            try:
                lock = zc.lockfile.LockFile('lockd.lock')
            except zc.lockfile.LockError:
                time.sleep(0.1)
                continue
            return lock

    def _resource_lock_name(self, resource):
        return os.path.join(self.lockdir, resource + '.resource.lock')

    @run_locked
    def lock(self, resource, client):
        resource_lock = self._resource_lock_name(resource)
        if os.path.exists(resource_lock):
            client = open(resource_lock, 'r').read().strip()
            raise Exception('Resource already locked by %r' % client)
        open(resource_lock, 'w').write(client)

    @run_locked
    def unlock(self, resource, client):
        resource_lock = self._resource_lock_name(resource)
        if not os.path.exists(resource_lock):
            raise Exception('Resource not locked')
        locked_by = open(resource_lock, 'r').read().strip()
        if client != locked_by:
            raise Exception(
                'Resource locked by %r cannot be unlocked by %r' % 
                (locked_by, client))
        os.unlink(resource_lock)


def main(host, port, directory):
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(
        (host, port), allow_none=True)
    server.register_introspection_functions()
    server.register_instance(Lockd(directory))
    server.serve_forever()
