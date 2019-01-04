'''Helper functions for operations on urls'''
from typing import Union, List, Dict, Optional, Any
import logging
import copy
import re

URL_REGEX = (
    r'^(?P<scheme>https?:\/\/)?'
    r'(?P<host>[a-zA-Z0-9][a-zA-Z0-9\.\-]*\.[a-zA-Z0-9\.\-]*(?<![\.\-]))'
    r'(?P<port>:[0-9]{1,5})?'
    r'(?P<path>[^?\s#&]*)'
    r'(?P<query>\?[^#\s&]*\=[^#\s&]*(?:&[^#\s&]*\=[^#\s&]*)*)?'
    r'(?P<fragment>[^\s]*)$'
)
DEFAULT_SCHEMA = ['scheme', 'host', 'port', 'path', 'query', 'fragment']
SECOND_LEVEL_DOMAINS = {sld.split('.')[0] for sld in (
    'ac.uk',
    'bl.uk',
    'british-library.uk',
    'co.uk',
    'cym.uk',
    'gov.uk',
    'govt.uk',
    'icnet.uk',
    'jet.uk',
    'lea.uk',
    'ltd.uk',
    'me.uk',
    'mil.uk',
    'mod.uk',
    'national-library-scotland.uk',
    'nel.uk',
    'net.uk',
    'nhs.uk',
    'nic.uk',
    'nls.uk',
    'org.uk',
    'orgn.uk',
    'parliament.uk',
    'plc.uk',
    'police.uk',
    'sch.uk',
    'scot.uk',
    'soc.uk',
    'wordpress.com'
)}

log = logging.getLogger(__name__)


def make_url(url: str, params: dict) -> str:
    '''
    Converts base url and params into a url
    Usage:
        >>> make_url('http://max.com/max', {'max': 1, 'what': 'no'})
        'http://max.com/max?max=1&what=no'
    '''
    if not params:
        return url
    param_str = '&'.join(f'{k}={v}' for k, v in sorted(params.items(), key=lambda x: x[0]))
    return f'{url}?{param_str}'

def query_to_dict(query_str: str) -> Dict[str, str]:
    '''
    Convert url query component to dictionary
    Usage:
        >>> query_to_dict('?max=max&foo=bar')
        {'max': 'max', 'foo': 'bar'}
        >>> query_to_dict('?')
        {}
    '''
    if len(query_str) > 1:
        return dict(q.split('=') for q in query_str[1:].split('&'))
    return {}

def query_to_str(query_dict: Dict[str, Any]) -> str:
    '''
    Convert a key-value mapping to url query format (with query keys sorted)
    Usage:
        >>> query_to_str({'max': 'max', 'foo': 'bar'})
        '?foo=bar&max=max'
    '''
    if query_dict:
        return '?' + '&'.join(
            f'{key}={value}'
            for key, value in sorted(
                query_dict.items(),
                key=lambda item: item[0]
            )
        )
    return ''

def no_www(url: str) -> str:
    '''
    Removes www. from the front of string if it's there
    Usage:
        >>> no_www('max.com')
        'max.com'
        >>> no_www('www.max.com')
        'max.com'
    '''
    if url[:4] == 'www.':
        return url[4:]
    return url

def parse(
        url: str,
        *,
        components: Optional[Union[str, List[str]]] = None,
        as_dict: bool = False
):
    '''
    Parses url and returns parsed url in requested format
    Arguments:
        url: url to be parsed
    Keyword arguments:
        components: how should the output be formatted (or which field to include in case of as_dict=True)
                    Choose from: scheme, host, port, path, query, fragment
        as_dict: should the parsed url be returned as dictionary?
                 If False it's going to be returned as string
    '''
    if components is None:
        components = copy.copy(DEFAULT_SCHEMA)
    elif not isinstance(components, list):
        components = components.split()
    _url = url.strip().replace(' ', '%20')
    if not url:
        return None
    match = re.search(URL_REGEX, _url)
    if match is None:
        return None
    components = [
        (component, match.group(component))
        for component in components
    ]
    if as_dict:
        components = dict(components)
        if 'query' in components and components['query'] is not None:
            components['query'] = query_to_dict(components['query'])
        return components
    return ''.join(comp_match for comp, comp_match in components if comp_match)

def iurl(url, query: Union[List[str], bool] = False):
    '''
    Convert url to a normalized form
    1. domain
    2. path
    3. query depending on the 'query' keyword argument
    Arguments:
        url: url to be normalized
    Keyword arguments:
        query: can be specified as either a list or a boolean
                - list: specify which query members should be included,
                        and in what order
                - bool: include full sorted query or do not include query (True/False)
    Usage:
        >>> iurl('https://inyourarea.co.uk/news/foo-bar-article?some=query&other=query2')
        'inyourarea.co.uk/news/foo-bar-article'
        >>> iurl('https://inyourarea.co.uk/news/foo-bar-article?some=query&other=query2', query=True)
        'inyourarea.co.uk/news/foo-bar-article?other=query2&some=query'
        >>> iurl('https://inyourarea.co.uk/news/foo-bar-article?some=query&other=query2', query=['some'])
        'inyourarea.co.uk/news/foo-bar-article?some=query'
    '''
    slugs = parse(url, components=['path'])
    if query:
        query_dict = parse(url, components=['query'], as_dict=True)['query']
        if isinstance(query, list):
            query_str = query_to_str({
                key: query_dict[key]
                for key in query
            })
        else:
            query_str = query_to_str(query_dict)
    else:
        query_str = ''
    _domain = domain(url, level=10)
    _iurl = f'{_domain}{slugs}{query_str}'
    if _iurl[-1] == '/':
        _iurl = _iurl[:-1]
    return _iurl


def domain(url, level=2):
    '''
    Extract domain from url
    Arguments:
        url:   url from which to extract the domain
        level: what is the maximum level of domain to capture
               i.e. level 1: .com, level 2: google.com, level 3: drive.google.com
               if None, no limit is applied
    Usage:
        >>> domain('https://drive.google.com')
        'google.com'
        >>> domain('https://drive.google.com', level=3)
        'drive.google.com'
    '''
    _domain = parse(url, 'host')
    if _domain is None:
        log.info('Url: %s could not be parsed!!!', url)
        return None
    _domain = no_www(_domain)
    if level is None:
        return _domain
    split = _domain.split('.')
    if len(split) >= 2 and split[-2] in SECOND_LEVEL_DOMAINS:
        level += 1
    level = min(level, len(split))
    return '.'.join(split[-level:])
