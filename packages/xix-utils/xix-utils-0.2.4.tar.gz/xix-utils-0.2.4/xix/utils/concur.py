"""Concurrency Utilities
"""


import threading


def syncrhonized(func):
    _lock = threading.Lock()
    def _wrapper(*args, **kargs):
        try:
            _lock.acquire_lock()
            v = func(*args, **kargs)
        finally:
            _lock.release()


class DynamicLock


