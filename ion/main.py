import re
from datetime import datetime, timedelta
from pytz import timezone
import hashlib
import time
from decimal import Decimal
import simplejson as json
import os
import math
import importlib
import logging
from typing import Sequence, Any, Dict, List, Tuple
from urllib.parse import urlparse

logger = logging.getLogger( __name__ )

url_regex = r'^(?P<schema>https?:\/\/)?(?P<domain>[a-zA-Z0-9][a-zA-Z0-9\.\-]*\.[a-zA-Z0-9\.\-]*(?<![\.\-]))(?P<port>:[0-9]{1,5})?(?P<slugs>[^?\s#&]*)(?P<params>\?[^#\s&]*\=[^#\s&]*(?:&[^#\s&]*\=[^#\s&]*)*)?(?P<anchor>[^\s]*)$'
# url_regex = r"^(https?:\/\/)?[^:\/\s&]+(:[0-9]*)?([^?\s#&]+)?(\?[^#\s&]*\=[^#\s&]*)*?(#[^\s?\=]*)?$"
# urlr = {
#     'scheme':   r'https?:\/\/',
#     'host':     r'[^:\/\s&]+',
#     'port':     r':[0-9]*',
#     'path':     r'(\/(?P<between>(?P<normal>[a-z\-\.\_\~\!\$\&\'\(\)\*\+\,\;\=\:\@0-9])|(?P<hex>\%[a-f0-9]{2}))+)+',
#     'query':    r'(\?[a-zA-Z0-9]+\=[a-zA-Z0-9]+)((\&|\;)[a-zA-Z0-9]+\=[a-zA-Z0-9]+)*',
#     'fragment': r'#[^\s?\=]*'
# }
# url_order = [ 'scheme', 'host', 'port', 'path', 'query', 'fragment' ]
# url_regex = ''.join( [ f'(P?<{schema_key}>{urlr[schema_key]})?' for schema_key in url_order ] )
# logger.info( url_regex )

def clean_link(link, schema):
    url = []
    if not isinstance(link, str):
        return link #None
    link = re.search(r'(http|www)[^ ]*', link).group(0) if ' ' in link.strip() else link
    regex = r'.*?(?P<schema>https?:\/\/)?(?P<domain>[^:\/ ]*)(?P<port>:[0-9]*)?(?P<slugs>.*)'
    match = re.search(regex, link)
    for e in schema if type(schema) is list else schema.split():
        url.append(str(match.group(e)))
    return "".join(url)

# def check_url(url):
#     schema = 'schema domain port slugs params anchor'.split(' ')
#     match = re.search(url_regex, url)
#     if match is None:
#         return False
#     for part in schema:
#         if schema

# def parse_url( url, schema = 'scheme host port path query fragment', no_www = False, as_dict = False, force_www = False ):
#     '''
#         Parses url and returns components matching schema spec
#         eg:
#             1 ) url - https://www.stable.inyourarea.co.uk/news/headline-goes-here#anchor?query=value
#                 parse_url( url, schema = 'schema' )
#                     returns 'https://'
#                 parse_url( url, schema = 'domain' )
#                     returns 'www.stable.inyourarea.co.uk'
#                 parse_url( url, schema = 'schema domain slugs' )
#                     returns 'https://www.inyourarea.co.uk/news/headline-goes-here'
#                 parse_url( url, schema = 'domain schema slugs' )
#                     returns 'www.inyourarea.co.ukhttps:///news/headline-goes-here'
#                 parse_url( url, schema = 'schema domain slugs', as_dict = True )
#                     returns {
#                         'schema': 'https://',
#                         'domain': 'www.stable.inyourarea.co.uk',
#                         'slugs': '/news/headline-goes-here'
#                     }
#         args:
#             - url
#         kwargs:
#             - schema    - which components to extract from the url ( default: 'schema domain port slugs params anchor' )
#             - no_www    - strip www. from domain name if occurs ( default: False )
#             - force_www - add www. to domain name if doesn't already occur ( default: False )
#             - as_dict   - return as dictionary of { schema_component: corresponding value } pairs ( default: False )
#     '''
#     url = url.strip()
#     if len( url ) == 0:
#         return url
#
#     url = url.replace( ' ', '%20' )
#     match = re.match( url_regex, url )
#     if not match:
#         raise ValueError( f'{url} is not a url' )
#
#     schema_keys = schema.split( ' ' ) if type( schema ) is str else schema
#     schema_values = []
#     for schema_key in schema_keys:
#         group = match.group( schema_key )
#         logger.debug( f'{schema_key}: {group}' )
#         if group:
#             schema_values.append( ( schema_key, group ) )
#     if as_dict:
#         return { k: v for k, v in schema_values }
#     return ''.join( [ v for _,v in schema_values ] )


def parse_url( url, schema = 'schema domain port slugs params anchor', no_www = False, dictionary = False, join = '', force_www = False, default_schema = 'https://' ):
    assert type(url) is str, '{} is not str but {}'.format( url, type( url ) )

    url = url.strip()
    if len(url) == 0:
        return None

    url = url.replace(' ', '%20')

    schema = schema.split(' ')

    match = re.search(url_regex, url)
    if match is None:
        return None
    matches = []

    for part in schema:
        try:
            current_match = match.group(part)
            if current_match is None:
                current_match = ''
            if part == 'domain':
                if no_www:
                    if current_match[:4] == 'www.':
                        current_match = current_match[4:]
                elif force_www:
                    if not current_match[:4] == 'www.':
                        subdomain_no = len(current_match.split('.')) - (2 if '.uk' == current_match[-3:] else 1)
                        if subdomain_no == 1 or force_www:
                            current_match = 'www.' + current_match
            matches.append((part, current_match))
        except Exception as e:
            print('---------------------------------')
            print('exception in url')
            print(url)
            print('current part', part)
            print('---------------------------------')
            return None
    matches = [ match if match[ 0 ] != 'schema' else ( match if match[ 1 ] else ( match[ 0 ], default_schema ) ) for match in matches ]
    if dictionary:
        matches = dict(matches)
        if 'params' in matches and matches['params'] is not None:
            if len(matches['params']) > 1:
                matches['params'] = dict([param.split('=') for param in matches['params'][1:].split('&')])
            else:
                matches['params'] = {}
        return matches
    else:
        matches = [match for part, match in matches]
        if join or join == '':
            return join.join(matches)
        else:
            return matches

def pop_schema( url ):
    if 'https://' == url[ :8 ]:
        return 'https://', url[ 8: ]
    elif 'http://' == url[ :7 ]:
        return 'http://', url[ 7: ]
    else:
        return '', url

def isdigit( char ):
    try:
        int( char )
        return True
    except ValueError:
        return False

def isalphanum( char ):
    return char.isalpha() or isdigit( char )

def ishostchar( char ):
    return isalphanum( char ) or char == '-'

def pop_host( url ):
    valid = False
    if not isalphanum( url[ 0 ] ):
        return None, url
    lastdot = False
    lastdash = False
    for i, s in enumerate( url[ 1: ] ):
        if s == '.':
            if lastdash or lastdot:
                return None, url
            lastdot = True
        elif isalphanum( s ):
            if not valid and lastdot:
                valid = True
            lastdot = False
            lastdash = False
        elif s in ( '/', ':', '?', '#' ):
            if lastdot or lastdash:
                return None, url
            return url[ :i+1], url[ i+1: ]
        elif s == '-':
            if lastdot:
                return None, url
            lastdash = True
            lastdot = False
        else:
            return None, url
    if valid and not lastdot:
        return url, ''
    return None, url

def pop_port( url ):
    if not len( url ):
        return '', ''
    if url[ 0 ] != ':':
        return '', url
    digits = False
    for i, s in enumerate( url[ 1: ] ):
        if isdigit( s ):
            digits = True
        elif s == '/':
            if digits:
                return url[ :i + 1 ], url[ i+1: ]
            else:
                return '', url
    if digits:
        return url, ''
    return '', url

def pop_path( url ):
    if not len( url ):
        return '', ''
    if url[ 0 ] != '/':
        return '', url
    for i in range( 1, len( url ) ):
        if url[ i ] in ( '#', '?' ):
            return url[ :i ], url[ i: ]
    return url, ''

def pop_query( url ):
    if not len( url ):
        return '', ''
    if url[ 0 ] != '?':
        return '', url
    for i in range( 1, len( url ) ):
        if url[ i ] == '#':
            return url[ :i ], url[ i: ]
    return url, ''

def pop_anchor( url ):
    if not len( url ):
        return '', ''
    if url[ 0 ] != '#':
        return '', url
    return url, ''

def parse_url_v2( url, schema = [ 'scheme', 'host', 'port', 'path', 'query', 'fragment' ], no_www = False, dictionary = False, force_www = False ):
    assert type( url ) is str, f'argument url: {url} is not str but {type(url)}!!!'

    url = url.strip()
    if len( url ) == 0:
        return url

    parsed = {}
    parsed[ 'scheme' ], url = pop_schema( url )
    parsed[ 'host' ], url = pop_host( url )
    if parsed[ 'host' ] is None:
        return None
    parsed[ 'port' ], url = pop_port( url )
    parsed[ 'path' ], url = pop_path( url )
    parsed[ 'query' ], url = pop_query( url )
    parsed[ 'fragment' ], url = pop_anchor( url )
    if len( url ) != 0:
        return None
    return ''.join( [ parsed[ scheme_bit ] for scheme_bit in schema ] )


def parse_url_v3( url, schema = [ 'scheme', 'host', 'port', 'path', 'query', 'fragment' ], no_www = False, dictionary = False, force_www = False ):
    if 'https://' == url[ :8 ] or 'http://' == url[ :7 ]:
        parsed = urlparse( url )
    else:
        parsed = urlparse( '//' + url )
    return parsed

def withoutquery(link):
    url = clean_link(link, 'schema domain slugs')
    i = url.find('?')
    return url[:i]


def queryfromlink(link):
    url = clean_link(link, 'slugs')
    i = url.find('?')
    parameters = []
    if i > -1:
        url = url[:i]
        parameters = [x.split('=') for x in url[i+1:].split('&')]
    return parameters


def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (hours, minutes, seconds)


def format_seconds(seconds, _format='%mm:%ss.%msms'):
    string = _format

    seconds_in_day = 60 * 60 * 24
    days = int(seconds / seconds_in_day)
    seconds = seconds % seconds_in_day

    seconds_in_hour = 60 * 60
    hours = int(seconds / seconds_in_hour)
    seconds = seconds % seconds_in_hour

    seconds_in_minute = 60
    minutes = int(seconds / seconds_in_minute)
    seconds = seconds % seconds_in_minute

    _seconds = int(seconds)
    seconds = seconds - _seconds

    mseconds = int(seconds * 1000)

    string = string.replace('%ms', '{:03d}'.format(mseconds))
    string = string.replace('%s', '{:02d}'.format(_seconds))
    string = string.replace('%m', '{:02d}'.format(minutes))
    string = string.replace('%h', '{:02d}'.format(hours))
    string = string.replace('%d', '{:02d}'.format(days))
    return string

def get_robots_txt(link):
    return clean_link(link, "schema domain") + "/robots.txt"


class Date(object):

    def __init__(self, date, type_=None):
        if date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None:
            self.date = date
        else:
            self.date = timezone('Europe/London').localize(date)
        self.datestr = self.datef(self.date)
        self.type = type_

    def __repr__(self):
        return self.datestr

    def after(self, days):
        delta = timedelta(days=days)
        return timezone('Europe/London').localize(datetime.now()) - delta < self.date

    def datef(self, date):
        return date.strftime('%Y-%m-%d %H:%M:%S%z')

    def datestr(self):
        return self.datef(date)

def md5(string):
    string = string.encode('utf-8')
    hash_object = hashlib.md5(string)
    return hash_object.hexdigest()
maxhash = md5

def sha1( string ):
    return hashlib.sha1( string.encode( 'utf-8' ) ).hexdigest()

def create_timestamp(date):
    return int(date.timestamp() * 1000)

def timestamp(ms=False, precision=False):
    return time.time() if precision else int(time.time() * (1000 if ms else 1))
ts = timestamp
get_timestamp = timestamp

def pts():
    return ts(precision=True)

def msts():
    return ts(ms=True)

def url2pub ( url ):
    words = [ "online", "herald", "northern", "express", "advertiser", "mail", "journal", "leader", "weekly", "courier", "today", "newsletter", "observer", "london", "reporter", "daily", "chronicle", "updates", "press", "standard", "times", "gazette", "guardian", "telegraph", "&", "and", "the", "news", "live", "echo", "citizen", "life" ]
    dmn = parse_url( url, 'domain' )
    dmn = dmn.replace( 'www.', '' ).split( '.' )[ 0 ]
    domain_chunks = dmn.split ( '-' )
    for word_i, word in enumerate ( words ):
        for i, domain_chunk in enumerate ( domain_chunks ):
            split = domain_chunk.strip () .split ( word )
            if len ( split ) > 1:
                for word_ in words [ word_i + 1 : ]:
                    if word_ in word:
                        words.remove ( word_ )
                split_i = 1
                while split_i < len ( split ):
                    split.insert ( split_i, word )
                    split_i += 2
                domain_chunks = [ chunk for chunk in domain_chunks [ : i ] + split + domain_chunks [ i + 1 : ] if len ( chunk ) > 0 ]
    return domain_chunks


def findall(string, sub, case_sensitive = False):
    if case_sensitive:
        string = string.lower()
        sub = sub.lower()
    alli = []
    accumulator = 0
    i = accumulator + string.find(sub)
    while i != accumulator - 1 and len(string) >= len(sub):
        alli.append(i)
        accumulator += i + len(sub)
        string = string[accumulator:]
        i = accumulator + string.find(sub)
    return alli


def chunk(iterable, target_size=None, num_chunks=None):
    if target_size is None:
        target_size = int(len(iterable) / num_chunks)
    for i in range(0, len(iterable), target_size):
        yield iterable[i:i+target_size]


class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, Decimal):
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)


def dedynamise( dict_ ):
    if type( dict_ ) is not dict:
        return dict_

    if len( dict_ ) == 1:
        key = list( dict_.keys() )[ 0 ]
        if key == 'S':
            return dict_[ key ]
        if key == 'N':
            return dict_[ key ]
        if key == 'L':
            return [ dedynamise( inner ) for inner in dict_[ key ] ]
        if key == 'M':
            return { dedynamise( inner_key ): dedynamise( inner_value ) for inner_key, inner_value in dict_[ key ].items() }
        if key == 'BOOL':
            return dict_[ key ]
        if key == 'NULL':
            return None
        return dict_
    else:
        return {
            dedynamise( key ): dedynamise( value ) for key, value in dict_.items()
        }


def ddb_key_size( key ):
    assert type( key ) is str, 'DDB keys must be strings and {} isnt\'t [{}]!'.format( key, type( key ) )
    return len( key )


def ddb_value_size( value ):
    vtype = type( value )
    if vtype is dict:
        sum = 3
        for k, v in value.items():
            sum += ddb_value_size( k ) + ddb_value_size( v )
        return sum
    elif vtype is list:
        sum = 3
        for i in value:
            sum += ddb_value_size( i )
        return sum
    elif vtype is str:
        return len( value.encode( 'utf-8' ) )
    elif vtype is int:
        return math.ceil( len( str( value ) ) / 2 ) + 1
    elif vtype is Decimal:
        sum = 1
        for v in str( value ).split( '.' ):
            sum += math.ceil( len( v ) / 2 )
        return sum
    elif value is None or vtype is bool:
        return 1
    else:
        raise ValueError( 'Unrecognised type: {} of {}'.format( vtype, value ) )


def to_kb( byte_count ):
    return byte_count / 1024


def ddb_stats( item ):
    sizes = dict( total = ddb_size( item ) )
    for k, v in item.items():
        sizes[ k ] = ddb_key_size( k ) + ddb_value_size( v )

    return json.dumps( sizes, indent = 4 )


def ddb_size( item ):
    if type( item ) is dict:
        sum = 0
        for k, v in item.items():
            sum += ddb_key_size( k ) + ddb_value_size( v )
        return sum
    else:
        raise ValueError( 'DDB item must be a dict!' )


def allequal(list_):
    iterator = iter(list_)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)


def sha1OfFile(filepath):
    sha = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            block = f.read(2**10) # Magic number: one-megabyte blocks.
            if not block: break
            sha.update(block)
        return sha.hexdigest()

def hash_dir(dir_path):
    hashes = []
    for path, dirs, files in os.walk(dir_path):
        for file in sorted(files): # we sort to guarantee that files will always go in the same order
            hashes.append(sha1OfFile(os.path.join(path, file)))
        for dir in sorted(dirs): # we sort to guarantee that dirs will always go in the same order
            hashes.append(hash_dir(os.path.join(path, dir)))
        break # we only need one iteration - to get files and dirs in current directory
    return str(hash(''.join(hashes)))


def hash_dir_contents(dir_path):
    hashes = {}
    for filename in os.listdir(dir_path):
        if not filename[0] == '.' and filename[-3:] == '.py':
            hashes[filename] = sha1OfFile(os.path.join(dir_path, filename))
    return hashes

def file2modulename(filename):
    return os.path.splitext(filename)[0].strip('/. ').replace(os.sep, '.')

def permutations_pairs(*args):
    for arg in args:
        assert hasattr(arg, '__iter__'), '{} is not iterable!'.format(arg)

    lists = [arg for arg in args]
    permutations = [[]]
    for list_ in lists:
        permutations_ = []
        for elem in list_:
            for permutation in permutations:
                permutations_.append(permutation + [elem])
        permutations = permutations_
    return permutations


def get(instance, attribute, default = False):
    if instance is None:
        return default
    return instance.get(attribute, default)

def path( d, path ):
    for path_step in path:
        d = d [ path_step ]
    return d

def update(d1, d2, lense = None):
    if lense is None:
        d1.update(d2)
        return d1
    elif type(lense) is str:
        d1[lense].update(d2)
        return d1
    else:
        temp = d1
        for l in lense:
            temp = temp[l]
        temp.update(d2)
        return d1


def findpath(d, path):
    if type(path) is str:
        return path in d
    else:
        intermediate = dict(**d)
        for path_chunk in path:
            if path_chunk in intermediate:
                intermediate = intermediate[path_chunk]
            else:
                return False
        return True

def add( i1, i2 ):
    return i1 + i2

def merge( d1, d2, op = add ):
    for key in d2:
        if key in d1:
            d1[ key ] = op( d1[ key ], d2[ key ] )
        else:
            d1[ key ] = d2[ key ]
    return d1

def sign( no ):
    return 1 if no > 0 else -1 if no < 0 else 0

def get_console_size(index = None):
    size = os.popen('stty size', 'r').read().split()
    if index is None:
        return size
    else:
        try:
            return int( size[ index ] )
        except IndexError:
            return None


def vertical_bar(char = '='):
    if char is None:
        return
    s = get_console_size( 1 )
    if s is None:
        return
    print( char * get_console_size( 1 ) )

def print_w_bars( *args, **kwargs ):
    vertical_bar()
    print( *args, **kwargs )
    vertical_bar()

def generate( item_s, n ):
    if type( item_s ) in ( tuple, list ):
        l = len( item_s )
    else:
        l = None
    for i in range( n ):
        if l is None:
            yield item_s
        else:
            yield item_s[ i % l ]

def uuid():
    return md5( str( ts( precision = True ) ) )



SLDs = tuple( [ sld.split( '.' )[ 0 ] for sld in (
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
) ] )

def domain( url, level = 2 ):
    '''
        Extract domain from url
        args:
            - url   - url from which to extract the domain
            - level - what is the maximum level of domain to capture
                      e.g. url: https://drive.google.com with level 2
                                returns google.com
                           url: https://drive.google.com with level 3
                                returns drive.google.com
                      if level is None, all levels of domain are going to be captured
    '''
    domain = parse_url( url, 'domain', no_www = True )
    if domain is None:
        logger.info( f'Url: {url} could not be parsed!!!' )
        return None
    if level is None:
        return domain
    split = domain.split( '.' )
    if level == 1:
        return split[ -1 ]
    else:
        if len( split ) == 1:
            return domain
        if split[ -2 ] in SLDs:
            domain = '.'.join( split[ -( level + 1 ): ] )
        else:
            domain = '.'.join( split[ -level: ] )
    return domain

def no_schema( url ):
    url = url.strip()
    if 'http://' == url[ :7 ]:
        return url[ 7: ]
    if 'https://' == url[ :8 ]:
        return url[ 8: ]
    return url


def substrings( string ):
    for i in range( len( string ) + 1 ):
        for j in range( i + 1, len( string ) + 1 ):
            yield string[ i:j ]



class JsonDict:
    fields: Sequence = ()
    defaults: Dict[str, Any] = {}
    def __init__( self, **kwargs ):
        if self.fields:
            for field in self.fields:
                try:
                    setattr( self, field, kwargs[ field ] )
                except KeyError:
                    try:
                        setattr( self, field, self.get_default( field ) )
                    except KeyError:
                        raise TypeError( f'Error converting: {json.dumps( kwargs, indent = 4 )}\nMissing required argument: {field}\nrequired args: {[ field for field in self.fields if field not in self.defaults ]}\nreceived args: {list(kwargs.keys())}' )
        else:
            self._my_fields = []
            for field, value in kwargs.items():
                self._my_fields.append( field )
                setattr( self, field, value )


    def get_default( self, field ):
        default_elem = self.defaults[ field ]
        if callable( default_elem ):
            return default_elem()
        else:
            return default_elem


    def __repr__( self ):
        return self.to_json( indent = 4, defaults = True )


    @classmethod
    def from_dict( cls, dct ):
        return cls( **dct )


    def to_obj( self, defaults = False ):
        dct = {}
        for field in ( self.fields or self._my_fields ):
            attr = getattr( self, field )
            try:
                attr = attr.to_obj( defaults = defaults )
            except AttributeError:
                pass
            if not defaults and field in self.defaults and attr == self.get_default( field ):
                continue
            dct[ field ] = attr
        return dct


    def to_json( self, defaults = False, **kwargs ):
        return json.dumps( self.to_obj( defaults = defaults ), **kwargs )



class JsonList:
    cls = None
    def __init__( self, *lst ):
        self._ = [ self.cls( **lst_elem ) for lst_elem in lst ]


    def __repr__( self ):
        return self.to_json( defaults = True, indent = 4 )


    def __getitem__( self, index ):
        return self._[ index ]


    def __iter__( self ):
        for lst_elem in self._:
            yield lst_elem

    def __len__( self ):
        return len( self._ )


    def append( self, item ):
        self._.append( item )


    def to_obj( self, defaults = False ):
        if self._ is None:
            return None
        obj = []
        for lst_elem in self._:
            try:
                obj.append( lst_elem.to_obj( defaults = defaults ) )
            except AttributeError:
                obj.append( lst_elem )
        return obj


    def to_json( self, defaults = True, **kwargs ):
        return json.dumps( self.to_obj( defaults = defaults ), **kwargs )


def join_params( params ):
    param_string = '&'.join( [ f'{key}={value}' for key, value in params.items() ] )
    if param_string:
        return f'?{param_string}'
    else:
        return param_string


def iurl( url, params = False ):
    slugs = parse_url( url, 'slugs' ).strip()
    if params:
        if type( params ) is list:
            extracted = parse_url( url, 'params', dictionary = True )
            param_string = join_params( { key: value for key, value in extracted[ 'params' ].items() if key in params } ).strip()
        else:
            param_string = parse_url( url, 'params' ).strip()
    else:
        param_string = ''
    iurl = ( domain( url, level = 10 ).strip() + slugs + param_string ).strip()
    if iurl[ -1 ] == '/':
        iurl = iurl[ :-1 ]
    return iurl


PERIOD_TYPES: Dict[str, int] = {
    'm': 30 * 24 * 60 * 60,
    'w': 7 * 24 * 60 * 60,
    'd': 24 * 60 * 60,
    'H': 60 * 60,
    'M': 60
}

PeriodChunk = Tuple[float, str]
PeriodChunks = List[PeriodChunk]

def split_period(period: str) -> PeriodChunks:
    no: str = ''
    split: PeriodChunks = []
    for char in period:
        if isdigit(char) or char == '.':
                no += char
        elif char in PERIOD_TYPES:
            split.append( ( float( no ), char, PERIOD_TYPES[char] ) )
            no = ''
        else:
            raise ValueError( f'Detected unexpected character {char} in period definition!' )
    return split

def period_to_ts( period, ms = True ):
    period = split_period( period )
    ago = int( ( 1000 if ms else 1 ) * sum( [ p[ 0 ] * PERIOD_TYPES[ p[ 1 ] ] for p in period ] ) )
    now = int( datetime.now().timestamp() * ( 1000 if ms else 1 ) )
    return now - ago, now

def period_to_sec(period: str) -> float:
    '''
    Converts period to number of seconds
    Args:
        period: amount of time in string form eg.: (1h, 2w, 3.2m2w12h)
    Returns:
        Number of seconds in period
    Examples:
        >>> print(period_to_sec('1h'))
        60.0
        >>> print(period_to_sec('1.5h'))
        90.0
        >>> print(period_to_sec('2w'))
        1209600.0
    '''
    period_chunks: PeriodChunks = split_period(period)
    chunk_seconds: List[float] = [chunk[0] * PERIOD_TYPES[chunk[1]] for chunk in period_chunks]
    return float(sum(chunk_seconds))
