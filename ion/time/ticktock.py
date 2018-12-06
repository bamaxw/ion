'''Separate interval module'''
from typing import Optional, Tuple, Dict
import threading


class TickTock:
    '''
        An object recording two types of events and a distance between them
        Events:
            tick: starts a sequence, all following tock events will
                  calculate an elapsed time to tick as a start point
            tock: continues a sequence, calculates elapsed times since last tock and last tick
        Args:
            format:     print results in formatted/unformatted way          default=True
            print_func: which print handler to default to [eg. logger.info] default=print
            tick:       do the first 'tick' on initialization               default=True
    '''
    def __init__(self, format: bool = True, print_func=print, tick: bool = True) -> None:
        self.format_f = format
        self.print = print_func
        if tick:
            self.tick()
        else:
            self.start = None
            self.end = None

    def tick(self) -> None:
        '''Record a tick event'''
        self.start = self.last = pts()

    def tock(self, format: Optional[bool] = None, print_func=None) -> Tuple[float, float]:
        '''
            Record a tock event and print out how much time elapsed since last tock and tick
            Args:
                format:     print results in formatted/unformatted way
                print_func: which print handler to use [eg. logger.info]
            Returns:
                Tuple of floats => time since last tock, time since last tick
        '''
        if format is None:
            format = self.format_f
        if print_func is None:
            print_func = self.print
        new_last = pts()
        old_last, self.last = self.last, new_last
        tock_elapsed = new_last - old_last
        tick_elapsed = new_last - self.start
        if format:
            tock_formatted = format_seconds(tock_elapsed)
            tick_formatted = format_seconds(tick_elapsed)
            msg = f'Elapsed {tock_formatted} / {tick_formatted} [last tock/last tick]'
        else:
            msg = f'{tock_elapsed}/{tick_elapsed}'
        print_func(msg)
        return tock_elapsed, tick_elapsed


_ticks_per_thread: Dict[int, TickTock] = {}
def tick(format: bool = True, print_func=print) -> None:
    '''
        Create a TickTock object for a current thread,
        or do a 'tick' for an existing one
        Args: look at ion.time.ticktock.TickTock.__init__
    '''
    global _ticks_per_thread
    ident: int = threading.get_ident()
    if ident in _ticks_per_thread:
        _ticks_per_thread[ident].tick()
    else:
        _ticks_per_thread[ident] = TickTock(format=format, print_func=print_func)

def tock(format: bool = True, print_func=print):
    '''
        Record a new 'tock' for a default TickTock object of a current thread
        [tock without a tick defaults to both tick and tock]
        Args: look at ion.time.ticktock.TickTock.tock
    '''
    global _ticks_per_thread
    ident = threading.get_ident()
    if ident not in _ticks_per_thread:
        _ticks_per_thread[ident] = TickTock(format=format, print_func=print_func)
    return _ticks_per_thread[ident].tock()


from . import pts, format_seconds
