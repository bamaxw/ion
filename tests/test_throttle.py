'''Testing module for ion.throttle'''
import unittest
import time
from ion.throttle import Throttle
from ion.benchmark import Measure

def dummy(naptime):
    '''Dummy function taking ~`naptime` sec to complete'''
    time.sleep(naptime)

def make_throttled(*a, **kw):
    return Throttle(*a, **kw)(dummy)


class ThrottleTestCase(unittest.TestCase):
    '''Test case for helpers.throttle'''
    def test_throttle_no_args_fails(self):
        '''Throttle initialized with no args should raise an Error'''
        with self.assertRaises(TypeError):
            Throttle()

    def test_throttle_no_args_decorator_fails(self):
        '''Throttle should fail if it decorates a function without being instantiated'''
        with self.assertRaises(TypeError):
            Throttle(dummy)

    def test_throttle_works(self):
        func = make_throttled(10)
        naptime = 0.01
        measure = Measure()
        with measure:
            for _ in range(20):
                func(naptime)
        self.assertGreater(measure.elapsed, 2)

    def test_throttle_interval(self):
        func = make_throttled(10, 1)
        naptime = 0.01
        measure = Measure()
        with measure:
            for _ in range(20):
                func(naptime)
        self.assertLess(measure.elapsed, 2)
        self.assertGreater(measure.elapsed, 1)
