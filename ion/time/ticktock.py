'''Separate interval module'''
from typing import Optional, Tuple, Dict, Callable
import threading
from . import pts, format_seconds


class TickTock:
    '''
        An object recording two types of events and a distance between them
        Events:
            tick: starts a sequence, all following tock events will
                  calculate an elapsed time to tick as a start point
            tock: continues a sequence, calculates elapsed times since last tock and last tick
        Args:
            print_func  -- which print handler to default to [eg. logger.info]
            format_func -- called every time a message should be issued to format elapsed time
            tick        -- do the first 'tick' on initialization
    '''
    def __init__(
            self,
            print_func: Optional[Callable] = print,
            format_func: Optional[Callable] = format_seconds,
            tick: bool = True
    ):
        self.format_func = format_func
        self.print_func = print_func
        self.start = self.last = self.end = None
        if tick:
            self.tick()

    def tick(self) -> None:
        '''Record a tick event'''
        self.start = self.last = pts()

    def tock(
            self,
            format_func: Optional[Callable] = None,
            print_func: Optional[Callable] = None
    ) -> Tuple[float, float]:
        '''
            Record a tock event and print out how much time elapsed since last tock and tick
            Args:
                format:     print results in formatted/unformatted way
                print_func: which print handler to use [eg. logger.info]
            Returns:
                Tuple of floats => time since last tock, time since last tick
        '''
        format_func = format_func or self.format_func
        print_func = print_func or self.print_func
        new_last = pts()
        old_last, self.last = self.last, new_last
        tock_elapsed = new_last - old_last
        tick_elapsed = new_last - self.start
        if print_func:
            if format_func:
                tock_formatted = format_func(tock_elapsed)
                tick_formatted = format_func(tick_elapsed)
                msg = f'Elapsed {tock_formatted}/{tick_formatted} [last tock/last tick]'
            else:
                msg = f'{tock_elapsed}/{tick_elapsed}'
            print_func(msg)
        return tock_elapsed, tick_elapsed


_ticks_per_thread: Dict[int, TickTock] = {}
def tick(
        format_func: Optional[Callable] = format_seconds,
        print_func: Optional[Callable] = print
) -> None:
    '''
        Create a TickTock object for a current thread,
        or do a 'tick' for an existing one
        Args: look at ion.time.ticktock.TickTock.__init__
    '''
    ident = threading.get_ident()
    if ident in _ticks_per_thread:
        _ticks_per_thread[ident].tick()
    else:
        _ticks_per_thread[ident] = TickTock(format_func=format_func, print_func=print_func, tick=True)

def tock(
        *,
        format_func: Optional[Callable] = format_seconds,
        print_func: Optional[Callable] = print
) -> Tuple[float, float]:
    '''
        Record a new 'tock' for a default TickTock object of a current thread
        [tock without a tick defaults to both tick and tock]
        Args: look at ion.time.ticktock.TickTock.tock
    '''
    ident = threading.get_ident()
    if ident not in _ticks_per_thread:
        _ticks_per_thread[ident] = TickTock(format_func=format_func, print_func=print_func)
    return _ticks_per_thread[ident].tock()
