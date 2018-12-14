'''Threading helper functions and classes'''
from typing import Optional, Callable, Any, Sequence
from itertools import zip_longest
from random import randrange
from functools import wraps
import contextlib
import threading
import logging

Target = Optional[Callable]
Args = Sequence[Any]
Kwargs = dict
ArgList = Sequence[Args]
KwargList = Sequence[Kwargs]


class ThreadManager:
    '''ThreadManager runs tasks in different threads, and manages a threadpool from a list'''
    def __init__(self, _id=None, max_threads=None, target=None):
        self._id = _id or '%05x' % randrange(16 * 5)
        self.max_threads = max_threads
        self.target = target
        self.log = logging.getLogger(f'{__name__}.ThreadManager-{self._id}')
        self.threads = set()

    def full(self) -> bool:
        '''Check whether the threadpool of ThreadManager is full'''
        return not self.max_threads is None and len(self.threads) >= self.max_threads

    def times(self, n: int, target: Target = None, args: Args = (), kwargs: Kwargs = None) -> None:
        '''Run a given function in a separate thread n times'''
        if kwargs is None:
            kwargs = {}
        target = target or self.target
        for _ in range(n):
            self.run(target=target, args=args, kwargs=kwargs)
        self.join()

    def foreach(self, target: Target = None, args: ArgList = (), kwargs: KwargList = ()):
        '''Runs a target function in a separate thread for each args-kwargs pair'''
        target = target or self.target
        iterator = zip_longest(tuple(args), tuple(kwargs))
        for a, kw in iterator:
            print(a, kw)
            self.run(target=target, args=a, kwargs=kw)
        self.join()

    def run(self, target: Target = None, args: Args = None, kwargs: Kwargs = None):
        '''
        Run a single thread within the managers environment
        Interface resembles that of threading.Thread
        '''
        if target is None:
            raise ValueError(f"Target can't be None!!!")
        if self.full():
            self.log.debug("Can't schedule another task, because thread-pool is full! Waiting...")
            self.wait()
        thread = ThreadManagerThread(target=target, args=args or (), kwargs=kwargs or {}, __manager=self)
        thread.start()

    def join(self):
        '''Join all threads belonging to the manager'''
        while self.threads:
            next(iter(self.threads)).join()

    def wait(self):
        '''Blocks until the ThreadManager's thread pool is not full'''
        while self.full():
            try:
                for thread in self.threads:
                    thread.join(timeout=0.05)
                    if not self.full():
                        return
            except RuntimeError as ex:
                print(str(ex))
                if str(ex) != 'Set changed size during iteration':
                    raise


class ThreadManagerThread(threading.Thread):
    '''Custom class extending Thread that disconnects from its manager on join'''
    def __init__(self, *a, **kw):
        __manager = kw.pop('__manager')
        super().__init__(*a, **kw)
        self.log = logging.getLogger(f'{__name__}.Thread-{self.ident}')
        self.__manager = __manager
        __manager.threads.add(self)

    def join(self, *a, **kw): # pylint: disable=arguments-differ
        '''
        Extends threading.Thread's join by checking whether
        the self thread is alive, and removing itself from managers threads
        '''
        super().join(*a, **kw)
        if not self.is_alive():
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('Not alive anymore! Removing self from manager!')
            self.__manager.threads.remove(self)


class WouldBlockError(Exception):
    '''
    Error signaling that a lock would block, but because
    of calling it from non_blocking_lock it isn't
    '''
    pass


@contextlib.contextmanager
def non_blocking_lock(lock: 'threading.Lock'):
    '''
    Acquires a lock passed as an argument, and raises WouldBlockError
    if the lock would block, without actually blocking
    Args:
        - lock: lock to acquire in non-blocking fashion
    '''
    if not lock.acquire(blocking=False):
        raise WouldBlockError
    try:
        yield lock
    finally:
        lock.release()

def synchronize(func: Callable) -> Callable:
    '''Allows only one thread at a time to access the decorated resource'''
    lock = threading.Lock()
    @wraps(func)
    def wrapper(*a, **kw):
        with lock:
            return func(*a, **kw)
    return wrapper
