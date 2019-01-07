'''Helper functions and classes for manipulating strings'''
from typing import Optional, List
import re

from .decorators import aslist
from .typing import MultilineStr
from .list import trim_list

@aslist
def ltrim_multiline(
        multi_str: MultilineStr,
        max_no: Optional[int] = None,
        char: str = ' '
):
    '''
    Takes a newline delimited string or list of strings
    and applies ltrim to each of its elements
    Usage:
        >>> ltrim_multiline('what\n    is\n going on')
        'what\nis\ngoing on'
        >>> ltrim_multiline('____max\n____codes\n_____helpers', char='_')
        'max\ncodes\nhelpers'
        >>> ltrim_miltiline('___max\n____codes', char='_', max_no=2)
        '_max\n__codes'
    '''
    if isinstance(multi_str, str):
        multi_str = multi_str.split('\n')
    for line in multi_str:
        max_index = len(line)
        if max_no is not None:
            max_index = min(max_index, max_no)
        if not max_index:
            yield line
            continue
        for i in range(max_index):
            if line[i] != char:
                yield line[i:]
                break
        else:
            yield line[max_index:]

def count_leading(string: str, char: str = ' ') -> int:
    '''
    Count leading characters in a strings
    Usage:
        >>> count_spaces('___max', char='_')
        3
        >>> count_spaces('_what____', char='_')
        1
    '''
    space_count = 0
    for character in string:
        if character == char:
            space_count += 1
        else:
            break
    return space_count

def clean_multiline(multiline_str: MultilineStr) -> str:
    '''
    Cleans multiline strings by removing all spaces from first non-empty line
    And removing at most the same number of spaces from any subsequent lines
    Usage:
        >>> clean_multiline("""
            Max is writing helpers
                And computer is compiling them
        """)
        'Max is writing helpers\n    And computer is compiling them'
    '''
    multiline_str = multiline_str.expandtabs(4)
    lines = trim_list(
        multiline_str.split('\n'),
        trim=''
    )
    if not lines:
        return ''
    space_count = count_leading(lines[0], char=' ')
    lines = ltrim_multiline(lines, space_count)
    return '\n'.join(lines)

def split(string: str, delimiters: MultilineStr = ' ') -> List[str]:
    '''
    Split string at multiple delimiters
    Usage:
        >>> split('abcadafaca', 'ab')
        ['c', 'd', 'f', 'c']
        >>> split('variable_with-many_stupid-delimiters', ['-', '_'])
        ['variable', 'with', 'many', 'stupid', 'delimiters']
    '''
    if isinstance(delimiters, str):
        regexp = delimiters
    else:
        try:
            regexp = '|'.join(list(delimiters))
        except TypeError:
            raise TypeError(
                ('Delimiters must be either a string or a different'
                 f' type of iterable! Instead found: {type(delimiters)!s}')
            )
    return re.split(regexp, string)

def isdigit(char: str) -> bool:
    '''
    Checks whether a character is a number
    Usage:
        >>> isdigit('m')
        False
        >>> isdigit('1')
        True
        >>> isdigit('_')
        False
    '''
    try:
        int(char)
        return True
    except ValueError:
        return False

def isalphanum(char: str) -> bool:
    '''
    Checks whether character is either a letter or a number
    Usage:
        >>> isalphanum('m')
        True
        >>> isalphanum('1')
        True
        >>> isalphanum('_')
        False
    '''
    return char.isalpha() or isdigit(char)

def list_substrings(string):
    '''
    Generate a list of all substrings of a given string
    Substrings can repeat
    '''
    for i in range(len(string) + 1):
        for j in range(i + 1, len(string) + 1):
            yield string[i:j]

def find_all(string, sub, case=False, overlap=True):
    '''Find all occurences of a substring in a string'''
    if not case:
        string = string.lower()
        sub = sub.lower()
    start_at = 0
    while start_at < len(string):
        next_index = string[start_at:].find(sub)
        if next_index < 0:
            return
        yield start_at + next_index
        if overlap:
            start_at += next_index + 1
        else:
            start_at += next_index + len(sub)
