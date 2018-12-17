'''Helper functions for filesystem management and navigation from python'''
from contextlib import contextmanager
from typing import List
import inspect
import os

DIR_STACK: List[str] = []


@contextmanager
def cd_to_script_location():
    '''Changes directory to a directory of a file from which this function was called'''
    file_dirname = get_dirname(1)
    pushd(file_dirname)
    yield file_dirname
    popd()

def pushd(dirname: str) -> None:
    '''Changes directory to dirname and saves previous directory to DIR_STACK'''
    DIR_STACK.append(os.getcwd())
    os.chdir(dirname)

def popd() -> None:
    '''Changes directory to the last one on DIR_STACK'''
    dirname = DIR_STACK.pop()
    os.chdir(dirname)

BAD_READ_FLAGS = set([*'wxa'])
def read(filename: str, flags: str = ''):
    '''Reads content from file with file context managed automatically'''
    if 'b' not in flags:
        flags += 't'
    flagset = set([*flags])
    if flagset.intersection(BAD_READ_FLAGS) != set():
        raise ValueError(f"Flags {flags} can't be used to read a file!")
    flagset.add('r')
    flags = ''.join(flagset)
    with open(filename, flags) as file:
        return file.read()

def get_dirname(__reset_stack=0, last=False):
    '''
    Get directory name of a file in stack
    In interactive mode returns current working directory
    Kwargs:
        - __reset_stack: how far up the stack should the function go in search for the file
        - last: get only directory name not the full name
    '''
    if is_interactive():
        dirname = os.getcwd()
    else:
        caller_stack = inspect.stack()[1+__reset_stack]
        caller_module = inspect.getmodule(caller_stack[0])
        caller_file = caller_module.__file__
        file_realname = os.path.realpath(caller_file)
        dirname = os.path.dirname(file_realname)
    if last:
        return dirname.split(os.path.sep)[-1]
    return dirname

def get_main_dir() -> str:
    '''Get directory of the main script'''
    import __main__ as main
    try:
        return main.__file__
    except AttributeError:
        return os.getcwd()

def is_interactive():
    '''Checks whether python session is run from interactive shell'''
    import __main__ as main
    return not hasattr(main, '__file__')
