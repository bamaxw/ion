'''Helper functions and classes useful for application level throttling'''
from collections import deque
from functools import wraps
import threading
import logging
import time

from .threading import non_blocking_lock, WouldBlockError
from .time import pts

log = logging.getLogger(__name__)

# TODO: Extrapolate speed and throttle before hitting interval
class Throttle:
    '''
    A decorator class for limiting rate of a particular function invocation
    Kwargs:
        - per_second: how many times a particular function can be called per second
                        use fractions for less than per second resolution
        - interval: limit rate to an average of per_second in a specified interval
    '''
    def __init__(self, per_second, interval=None):
        if interval is None:
            interval = 1 / per_second
        self.per_second = per_second
        self.interval = interval
        self.invocations = deque()
        self.lock = threading.Lock()

    def __call__(self, func):
        '''Wrap a function into the throttling _wrapper'''
        @wraps(func)
        def _wrapper(*a, **kw):
            retries = 0
            while True:
                average = self.average_in_interval()
                log.info('Average is %d', average)
                if average >= self.per_second:
                    log.info('Sleeping')
                    sleep_for = min(
                        (self.interval / self.per_second) * (2 ** retries),
                        self.interval
                    )
                    time.sleep(sleep_for)
                    retries += 1
                else:
                    try:
                        with non_blocking_lock(self.lock):
                            self.invocations.append(pts())
                            return func(*a, **kw)
                    except WouldBlockError:
                        continue
        return _wrapper

    def remove_old(self):
        '''Removes old invocations from memory'''
        remove_before = pts() - self.interval
        while True:
            try:
                invocation_ts = self.invocations.popleft()
                if invocation_ts >= remove_before:
                    self.invocations.appendleft(invocation_ts)
                    break
            except IndexError:
                break

    def average_in_interval(self):
        '''Calculates an average number of invocations per second in a given interval'''
        self.remove_old()
        return len(self.invocations) / self.interval



# stats = {'last_time': 0}
# lock = threading.Lock()
#
# def throttle(rate):
#     def realthrottle(function):
#         def evenmorerealthrottle(*args, **kwargs):
#             global stats, lock
#             while True:
#                 try:
#                     if pts() <= stats['last_time'] + rate:
#                         pass
#                     else:
#                         with non_blocking_lock(lock):
#                             stats['last_time'] = pts()
#                         return function(*args, **kwargs)
#                 except WouldBlockError:
#                     pass
#         return evenmorerealthrottle
#     return lambda function: realthrottle(function)
