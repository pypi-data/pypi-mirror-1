"""
    memcached_lock
    ~~~~~~~~~~~~~~

    Implements a distributed transaction using memcached or
    a memcached compatible storage.

    Example::

        from __future__ import with_statement
        import memcache
        from memcached_lock import dist_lock

        client = memcache.Client(['127.0.0.1:11211'])
        with dist_lock('test', client):
            print 'Is there anybody out there!?'

"""

from __future__ import with_statement
from contextlib import contextmanager
import time

DEFAULT_EXPIRES = 15
DEFAULT_RETRIES = 5

@contextmanager
def dist_lock(key, client):
    try:
        _acquire_lock(key, client)
        yield
    finally:
        _release_lock(key, client)

def _acquire_lock(key, client):
    for i in xrange(0, DEFAULT_RETRIES):
        stored = client.add(key, 1, DEFAULT_EXPIRES)
        if stored:
            return
        print 'Sleeipng for %s' % ((2**i) / 3.5)
        time.sleep((2**i) / 2.5)
    raise Exception('Could not acquire lock for %s' % key)

def _release_lock(key, client):
    client.delete(key)
