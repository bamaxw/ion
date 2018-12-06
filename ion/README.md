# ion

# ion._class
Useful helper classes and class helpers
## ToDict
```python
ToDict(self)
```

ToDict implements to_dict method which
returns a dictionary representation of
an inheriting class instance
Class level attributes:
    - fields: list of fields to be included in dict representation

## StrictToDict
```python
StrictToDict(self)
```
Same as ToDict but allowing dict keys to be only from _fields
## ToJson
```python
ToJson(self)
```

ToJson class implements to_json method which takes
a dict representation of an inheriting class (self.to_dict())
and converts it to json encoded string

## PPrintable
```python
PPrintable(self)
```

PPrintable implements pprint and pformat
And changes behaviour of __str__ and __repr__ to use pformat

## DCDict
```python
DCDict(self, /, *args, **kwargs)
```

Data Class Dict
Overwrite this with a dataclass to gain access to to_dict() method
that basically acts as a asdict(self)

## singleton
```python
singleton(cls: Type)
```

Any class decorated with this decorator will have only one instance
After first initialization, any subsequent attempts to initialize the
same class will result in its original instance being returned

## make_property
```python
make_property(cls: Type, prop_name: str, default=None, getter=True, setter=True)
```

Creates a getter and setter properties on a class object
    for a given property name

# ion._import
Functions and classes helping with import functionalities
## load_object
```python
load_object(path: str)
```

Load an object from path
    e.g. 'helpers._import.load_object' will load this function object

## get_caller_module
```python
get_caller_module(__reset_stack=0)
```
Return module of this function's caller's caller
# ion.args

## ArgSpec
```python
ArgSpec(self, name: str, short: Union[str, NoneType] = None, long: Union[str, NoneType] = None, index: Union[int, NoneType] = None, type: str = <class 'str'>, default: Union[Any, NoneType] = None, required: bool = True, provided: bool = False, flag: bool = False, named: bool = True, values: Union[Iterable, NoneType] = None, description: str = '') -> None
```
ArgSpec(name: str, short: Union[str, NoneType] = None, long: Union[str, NoneType] = None, index: Union[int, NoneType] = None, type: str = <class 'str'>, default: Union[Any, NoneType] = None, required: bool = True, provided: bool = False, flag: bool = False, named: bool = True, values: Union[Iterable, NoneType] = None, description: str = '')
# ion.bash

## colors
```python
colors(self, /, *args, **kwargs)
```

# ion.benchmark
Helper functions and classes for code banchmarking
## meantime
```python
MeanTime.__call__(func)
```
Use this decorator to record elapsed times for a function func
## MeanTime
```python
MeanTime(self)
```
A decorator class for recording functions' elapsed times
## Measure
```python
Measure(self)
```
Context class which calculates elapsed time of its block
## timeit
```python
timeit(func)
```
This decorator logs elapsed time (DEBUG) after every run
# ion.cache
Functions and classes helping with application-level caching and memoization
## minute_memoize
```python
MemoizeWithTimeout.__call__(func)
```

## TsValue
```python
TsValue(self, /, *args, **kwargs)
```
TsValue(value, timestamp)
## MemoizeWithTimeout
```python
MemoizeWithTimeout(self, timeout: int = 60)
```

Use this class to memoize a functions result for a certain period of time
Class attributes:
    - _per_func_cache: stores a function result in a dictionary where
                          key is tuple(args, tuple(sorted(kwargs.items()))) tuple, and
                          value is TsValue with value being return value and ts being timestamp when it happened
    - _timeouts: stores timeout value for each of registered functions

## create_minute_memoize
```python
create_minute_memoize(no_minutes: float)
```
Creates MemoizeWithTimeout with timeout equal no_minutes minutes
## create_minute_memoize
```python
create_minute_memoize(no_minutes: float)
```
Creates MemoizeWithTimeout with timeout equal no_minutes minutes
## create_minute_memoize
```python
create_minute_memoize(no_minutes: float)
```
Creates MemoizeWithTimeout with timeout equal no_minutes minutes
# ion.decorators
Module containing various decorators
## aslist
```python
aslist(func)
```
Converts generator function into a function that returns list
## asdict
```python
asdict(func)
```

Converts generator function into a function that returns dict
Wrapped function must generate a key-value tuples

## logreturn
```python
logreturn(func)
```
Runs a wrapped function and logs its return value
## tail_call_optimized
```python
tail_call_optimized(func)
```

This function decorates a function with tail call
optimization. It does this by throwing an exception
if it is it's own grandparent, and catching such
exceptions to fake the tail call optimization.

This function fails if the decorated
function recurses in a non-tail context.

## TailRecurseException
```python
TailRecurseException(self, args, kwargs)
```

Exception thrown by tail_call_optimized to communicate a recursive call
being its own grandparent

# ion.dict
Helper functions for operations on dictionaries
## path
```python
path(path, dct, default=Ellipsis)
```

Get dictionary value at path
Args:
    - path: path to where the value should be taken from e.g.: ['item'] or ['item', 'attr_name']
    - dct: dictionary to get the value from
Kwargs:
    - default: a value to be returned if a given path doesn't exist
Usage:
    >>> path(['item'], {'item': 100})
    100
    >>> path(['item', 'attr_name'], {'item': 100}, default=None)
    None
    >>> path(['item', 'attr_name'], {'item': {'attr_name': 'max'}})
    'max'

## set_path
```python
set_path(path, value, dct, inplace=True)
```

Set path of a dictionary to a particular value
Args:
    - path: path to where the value should be set e.g.: ['item'] or ['item', 'attr_name']
    - value: which value should be set at the path
    - dct: dictionary to be updated
Kwargs:
    - inplace: if True this function mutates the original object
Usage:
    >>> set_path(['item'], 100, {})
    {'item': 100}
    >>> set_path(['item', 'attr_name'], 100, {'item': {'attr_name': 0}})
    {'item': {'attr_name': 100}}

## apply
```python
apply(dct: dict, key=<function <lambda> at 0x10385e950>, value=<function <lambda> at 0x10385e9d8>, item=None) -> dict
```

Return a new dictionary with keys and values changed according to provided functions
Arguments:
    key: apply this function to each key in the dictionary
    value: apply this function to each value in the dictionary
    item: ignore key and value and apply both function to a tuple of (key, value)

# ion.dynamodb
Helper functions facilitating boto3 usage
## dedynamise
```python
dedynamise(dct)
```
Dedynamise typed dictionary returned from DDB
## DDBSize
```python
DDBSize(self, /, *args, **kwargs)
```
Calculate DDB Size of different python objects
# ion.env
Helper functions for resolving and dealing with env
## get_env
```python
get_env() -> str
```
Get env variable from either arguments or environmental variables
## get_env_from_args
```python
get_env_from_args() -> Union[str, NoneType]
```
Get env variable from args (-e or --env)
## get_env_from_vars
```python
get_env_from_vars() -> Union[str, NoneType]
```
Get env variable from environmental variables (ENVIRONMENT or ENV)
## is_valid_env
```python
is_valid_env(env) -> bool
```
Check whether environment is valid
# ion.files
Helper functions for filesystem management and navigation from python
## cd_to_script_location
```python
cd_to_script_location()
```
Changes directory to a directory of a file from which this function was called
## pushd
```python
pushd(dirname: str) -> None
```
Changes directory to dirname and saves previous directory to DIR_STACK
## popd
```python
popd() -> None
```
Changes directory to the last one on DIR_STACK
## read
```python
read(filename: str, flags: str = '')
```
Reads content from file with file context managed automatically
## get_dirname
```python
get_dirname(__reset_stack=0, last=False)
```

Get directory name of a file in stack
In interactive mode returns current working directory
Kwargs:
    - __reset_stack: how far up the stack should the function go in search for the file
    - last: get only directory name not the full name

## is_interactive
```python
is_interactive()
```
Checks whether python session is run from interactive shell
# ion.hash
Helper functions and classes for hashing
## genhash
```python
genhash(string: str, hashfunc, asbytes=False) -> str
```
Simplified hashlib hashing
## hashfile
```python
hashfile(filepath: str, hash_object, buffer_size: int = 65536, asbytes=False) -> str
```

Hash contents of a file
Arguments:
    filepath:    path to a file which contents are going to be hashed
    hash_object: hash object implementing .update() method [e.g. hashlib.sha1()]
    buffer_size: arbitrary buffer size to use for buffering file

## hash_dir
```python
hash_dir(dirpath: str, hash_type: str, recursive=True, asbytes=False)
```

Hash contents of a directory
Arguments:
    dirpath: path to a directory
    hash_type: name a of a hash to be used [e.g. 'sha1']
    recursive: should the hash be calculated recursively

# ion.injector
Helper module defining functions and classes associated with injectors
## Injector
```python
Injector(bindings: Union[Dict[Union[Type, str], Any], NoneType] = None)
```
Simple implementation of dependecy injector
## inject
```python
inject(*dependencies)
```

Decorator factory creating a decorator which injects specified dependencies
Args:
    - *dependencies: list of keys at which dependencies are bound in Injector
                        keys can be either strings or types, depending how the
                        resource was bound to the injector
Usage:
    >>> @inject(FooService, BarService, 'max', 'python')
    >>> def do_something(arg1, arg2, foo_service, bar_service, max, python, **kwargs)
    >>>     pass

# ion.itemstore
InYourArea ItemStore helper functions and classes
## Publisher
```python
Publisher(self, name: str, uuid: Union[str, NoneType] = None, settings: dict = <factory>) -> None
```

ItemStore Publisher representing Harvester Publisher
Attributes:
    ---

## SimplifiedPublication
```python
SimplifiedPublication(self, url: str, publisher: Union[str, NoneType] = None, mode: Union[str, NoneType] = 'smart') -> None
```
ItemStore Simplified Publication representing Harvester Publication
## Publication
```python
Publication(self, name: str, domain: str, publisher: str, sections: list, uuid: Union[str, NoneType] = None, config: dict = <factory>, parent_iid: Union[str, NoneType] = None, parent_type: Union[str, NoneType] = None, iid: Union[str, NoneType] = None, settings: dict = <factory>) -> None
```
ItemStore Publication representing Harvester Publication
## Section
```python
Section(self, url: str, job: dict, name: Union[str, NoneType] = None, settings: dict = <factory>, uuid: Union[str, NoneType] = None) -> None
```

ItemStore Section representing Publication's section
Attributes:
    name: Name of the section (can be None)
    url: url of the section consisting of only domain and slugs e.g. inyourarea.co.uk/news/ion-with-dataclasses
    uuid: md5 hashed url (used for de-duplication)
    job: job definition associated with the section
    settings: settings for this particular section

## is_valid_id
```python
is_valid_id(_id: str) -> bool
```
Checks whether itemstore id or iid is valid
## Paginator
```python
Paginator(self, url, total_count: Union[int, NoneType] = None, batch_size: int = 500, period: Union[str, NoneType] = None, max_retries: int = 5, **kwargs)
```

# ion.json
Module containing helper functions and classes associated with json module and format
## load
```python
load(payload: Union[str, bytes]) -> Any
```
Converts json string or bytes to its python representation
## aws_load
```python
aws_load(payload: Union[str, bytes]) -> Any
```
Converts json string or bytes and converts floats to decimal.Decimal
## dump
```python
dump(payload: Any) -> str
```
Converts python data structure into a json encoded string
# ion.list
Helper functions for operations on sequences
## T
Type variable.

Usage::

  T = TypeVar('T')  # Can be anything
  A = TypeVar('A', str, bytes)  # Must be str or bytes

Type variables exist primarily for the benefit of static type
checkers.  They serve as the parameters for generic types as well
as for generic function definitions.  See class Generic for more
information on generic types.  Generic functions work as follows:

  def repeat(x: T, n: int) -> List[T]:
      '''Return a list containing n references to x.'''
      return [x]*n

  def longest(x: A, y: A) -> A:
      '''Return the longest of two strings.'''
      return x if len(x) >= len(y) else y

The latter example's signature is essentially the overloading
of (str, str) -> str and (bytes, bytes) -> bytes.  Also note
that if the arguments are instances of some subclass of str,
the return type is still plain str.

At runtime, isinstance(x, T) and issubclass(C, T) will raise TypeError.

Type variables defined with covariant=True or contravariant=True
can be used do declare covariant or contravariant generic types.
See PEP 484 for more details. By default generic types are invariant
in all type variables.

Type variables can be introspected. e.g.:

  T.__name__ == 'T'
  T.__constraints__ == ()
  T.__covariant__ == False
  T.__contravariant__ = False
  A.__constraints__ == (str, bytes)

Note that only type variables defined in global scope can be pickled.

## trim_list
```python
trim_list(lst: Iterable[~T], trim: ~T = '') -> Iterable[~T]
```

Look at the beginning and end of a list and trim elements that are equal to trim
Args:
    - lst: list to be trimmed
    - trim: elements of lst at the beginning and the end equal to this argument will be removed
Usage:
    >>> trim_list(['', 'max', ''])
    ['max']
    >>> trim_list(['max', 'max', '', '', 'max'], trim='max')
    ['', '']

## as_list
```python
as_list(arg: Union[~T, List[~T]], tuples: bool = True) -> Iterable[~T]
```

Converts passed argument to list if it's not already a list
Args:
    - arg: argument to be converted to list
Kwargs:
    - tuples: whether to accept tuples as lists if set to False it will wrap tuple in list
Usage:
    >>> as_list('max')
    ['max']
    >>> as_list(['max'])
    ['max']
    >>> as_list(('max',))
    ('max',)
    >>> as_list(('max',), tuples=False)
    [('max',)]

## allequal
```python
allequal(lst: Iterable) -> bool
```

Check whether a sequence contains elements that are all equal to each other
>>> allequal([1,2,3])
False
>>> allequal([])
True
>>> allequal([1])
True
>>> allequal([1,1,1])
True

## chunk
```python
chunk(lst: Iterable[~T], size: int) -> Generator[Iterable[~T], NoneType, NoneType]
```
Split an iterable into chunks of size `size`
## chunk_into
```python
chunk_into(lst: Iterable[~T], chunks: int) -> Generator[Iterable[~T], NoneType, NoneType]
```
Split an iterable into `chunks` chunks
# ion.logging
Helper functions and classes facilitating logging module usage
## get_level
```python
get_level(level: str = 'WARNING') -> int
```

Get int representation of a log level from logging module
Usage:
    >>> get_level('WARNING')
    30
    >>> get_level('INFO')
    20

# ion.math
Helper functions completing built-in math module
## mean
```python
mean(numbers: List[Union[int, float]]) -> Union[float, NoneType]
```
Calculate mean of list of numbers
## sign
```python
sign(number: Union[int, float]) -> int
```
Return sign of a number
# ion.nlp
NLP helper functions and classes
## get_stemmer
```python
get_stemmer(lang: str) -> nltk.stem.snowball.SnowballStemmer
```
Get a word stemmer for a particular language
## get_spacy_nlp
```python
get_spacy_nlp(lang: str)
```
Get spaCy nlp for a given language
## past_tense
```python
past_tense(text: str) -> str
```

Convert word to its past tense form
Usage:
    >>> past_tense('compute')
    'computed'
    >>> past_tense('max out')
    'maxed out'

## singular
```python
singular(word: str, lang: str = 'en') -> str
```
Convert word to its singular form
## plural
```python
plural(word: str) -> str
```

Convert a word to its plural form
Usage:
    >>> plural('computer')
    'computers'
    >>> plural('max')
    'maxes'

## camel_case_to_words
```python
camel_case_to_words(camel_case_var: str) -> List[str]
```

Convert camel case word into a list of words
Usage:
    >>> camel_case_to_words('whatIsGoingOn')
    ['what', 'Is', 'Going', 'On']
    >>> camel_case_to_words('whoEvenUsesCamelCase')
    ['who', 'Even', 'Uses', 'Camel', 'Case']

## var_to_words
```python
var_to_words(var: str) -> str
```

Convert variable name into words
Usage:
    >>> var_to_words('ugc-posts')
    ['ugc', 'posts']
    >>> var_to_words('very_small_variable')
    ['very', 'small', 'variable']
    >>> var_to_words('verySmallVariable')
    ['very', 'small', 'variable']

## capitalize_each
```python
capitalize_each(_str: Union[str, List[str]]) -> str
```

Capitalize each word in list or string
Usage:
    >>> capitalize_each(['max', 'codes', 'helpers'])
    ['Max', 'Codes', 'Helpers']
    >>> capitalize_each('et al acclaimed most cited researcher')
    ['Et', 'Al', 'Acclaimed', 'Most', 'Cited', 'Researcher']

## ordinal
```python
ordinal(n: int) -> str
```

Converts integer into an ordinal string
Usage:
    >>> ordinal(1)
    '1st'
    >>> ordinal(10)
    '10th'

## sentences
```python
sentences(text: str, lang: str = 'en') -> List[str]
```
Splits string into sentences
## words
```python
words(text: str, lang: str = 'en', punct: bool = False) -> List[str]
```
Split string into words
## tokens
```python
tokens(text: str, lang: str = 'en') -> list
```
Split string into tokens
## ari
```python
ari(text: str)
```
Calculate automated readability index of text
# ion.prime
Helper functions facilitating prime calculations
## legendre
```python
legendre(a, m)
```

Calculates legendre symbol (a|m)
note: returns m-1 if a is a non-residue, instead of -1

## is_strong_probable_prime
```python
is_strong_probable_prime(n, b=2)
```
Checks whether a number n is a strong probable prime
## is_lucas_probable_prime
```python
is_lucas_probable_prime(n, D)
```

Checks whether a number is Lucas probable prime
assumes D = 1 (mod 4), (D|n) = -1

# ion.requests
Requests helper functions and classes
## get_header
```python
get_header(response: 'requests.Response', header: str, default=None)
```
Get header from response
## restart_on_connerr
```python
restart_on_connerr(func)
```

Method decorator catches ConnectionError and resets object's 'session'
Must be called on a method!

## Requests
```python
Requests(self, max_retries=5, retry_on=(), accept_on=(), raise_on_status=False)
```

Wrapper class mimicking requests module functionalities
Implementing default layer of error handling and retry policy
Arguments:
    max_retries:     how many times should a request be retries on bad status code
    retry_on:        which codes should be added to default list of status codes on which
                     retry is triggered
                         default list: 400, 403, 500, 502, 503, 504
    accept_on:       which codes should be removed from default list of status codes on which
                     retry is triggered
    raise_on_status: after the number of retries is greater than max_retries,
                     should an error be thrown or rather a bad response returned

# ion.setup
Helper functions for package setup
## get_version
```python
get_version(package_name=None, filename=None)
```
Find __version__ in file
# ion.string
Helper functions and classes for manipulating strings
## ltrim_multiline
```python
ltrim_multiline(multi_str: Union[str, List[str]], max_no: Union[int, NoneType] = None, char: str = ' ')
```

Takes a newline delimited string or list of strings
and applies ltrim to each of its elements
Usage:
    >>> ltrim_multiline('what
is
going on')
    'what
is
going on'
    >>> ltrim_multiline('____max
____codes
_____helpers', char='_')
    'max
codes
helpers'
    >>> ltrim_miltiline('___max
____codes', char='_', max_no=2)
    '_max
__codes'

## count_leading
```python
count_leading(string: str, char: str = ' ') -> int
```

Count leading characters in a strings
Usage:
    >>> count_spaces('___max', char='_')
    3
    >>> count_spaces('_what____', char='_')
    1

## clean_multiline
```python
clean_multiline(multiline_str: Union[str, List[str]]) -> str
```

Cleans multiline strings by removing all spaces from first non-empty line
And removing at most the same number of spaces from any subsequent lines
Usage:
    >>> clean_multiline("""
        Max is writing helpers
            And computer is compiling them
    """)
    'Max is writing helpers
And computer is compiling them'

## split
```python
split(string: str, delimiters: Union[str, List[str]] = ' ') -> List[str]
```

Split string at multiple delimiters
Usage:
    >>> split('abcadafaca', 'ab')
    ['c', 'd', 'f', 'c']
    >>> split('variable_with-many_stupid-delimiters', ['-', '_'])
    ['variable', 'with', 'many', 'stupid', 'delimiters']

## isdigit
```python
isdigit(char: str) -> bool
```

Checks whether a character is a number
Usage:
    >>> isdigit('m')
    False
    >>> isdigit('1')
    True
    >>> isdigit('_')
    False

## isalphanum
```python
isalphanum(char: str) -> bool
```

Checks whether character is either a letter or a number
Usage:
    >>> isalphanum('m')
    True
    >>> isalphanum('1')
    True
    >>> isalphanum('_')
    False

## list_substrings
```python
list_substrings(string)
```

Generate a list of all substrings of a given string
Substrings can repeat

## find_all
```python
find_all(string, sub, case=False, overlap=True)
```
Find all occurences of a substring in a string
# ion.threading
Threading helper functions and classes
## ThreadManager
```python
ThreadManager(self, _id=None, max_threads=None, target=None)
```
ThreadManager runs tasks in different threads, and manages a threadpool from a list
## ThreadManagerThread
```python
ThreadManagerThread(self, *a, **kw)
```
Custom class extending Thread that disconnects from its manager on join
## WouldBlockError
```python
WouldBlockError(self, /, *args, **kwargs)
```

Error signaling that a lock would block, but because
of calling it from non_blocking_lock it isn't

## non_blocking_lock
```python
non_blocking_lock(lock: 'threading.Lock')
```

Acquires a lock passed as an argument, and raises WouldBlockError
if the lock would block, without actually blocking
Args:
    - lock: lock to acquire in non-blocking fashion

# ion.throttle
Helper functions and classes useful for application level throttling
## Throttle
```python
Throttle(self, per_second, interval=None)
```

A decorator class for limiting rate of a particular function invocation
Kwargs:
    - per_second: how many times a particular function can be called per second
                    use fractions for less than per second resolution
    - interval: limit rate to an average of per_second in a specified interval

# ion.time
Root time module containing helper functions and classes for dealing with time and dates
## ts
```python
ts()
```
Get current UNIX timestamp in seconds as an integer
## pts
```python
pts()
```
Get current UNIX timestamp in seconds as a fraction
## msts
```python
msts()
```
Get current UNIX timestamp in milliseconds as an integer
## dt_to_ts
```python
dt_to_ts(date_time: 'datetime.datetime')
```
Convert datetime object to UNIX timetsamp
## to_midnight
```python
to_midnight(date_time: 'datetime.datetime')
```

Round the provided datetime object to the last day
Usage:
    >>> to_midnight(datetime.strptime('14 Aug 1993 10:21', '%d %b %Y %H:%M')).strftime('%d %b %Y %H:%M')
    "14 Aug 1993 00:00"

## format_seconds
```python
format_seconds(seconds: float, _format: str = '%mm:%ss.%msms')
```

Formats a number of seconds into a formatted string
Usage:
    >>> format_seconds(10)
    '00m:10s.000ms'
    >>> format_seconds(110.24)
    '01m:50s.240ms'
    >>> format_seconds(3601.52, _format='%h:%m:%s.%ms')
    '01:00:01.520'

# ion.typing
Helper types
## T
Type variable.

Usage::

  T = TypeVar('T')  # Can be anything
  A = TypeVar('A', str, bytes)  # Must be str or bytes

Type variables exist primarily for the benefit of static type
checkers.  They serve as the parameters for generic types as well
as for generic function definitions.  See class Generic for more
information on generic types.  Generic functions work as follows:

  def repeat(x: T, n: int) -> List[T]:
      '''Return a list containing n references to x.'''
      return [x]*n

  def longest(x: A, y: A) -> A:
      '''Return the longest of two strings.'''
      return x if len(x) >= len(y) else y

The latter example's signature is essentially the overloading
of (str, str) -> str and (bytes, bytes) -> bytes.  Also note
that if the arguments are instances of some subclass of str,
the return type is still plain str.

At runtime, isinstance(x, T) and issubclass(C, T) will raise TypeError.

Type variables defined with covariant=True or contravariant=True
can be used do declare covariant or contravariant generic types.
See PEP 484 for more details. By default generic types are invariant
in all type variables.

Type variables can be introspected. e.g.:

  T.__name__ == 'T'
  T.__constraints__ == ()
  T.__covariant__ == False
  T.__contravariant__ = False
  A.__constraints__ == (str, bytes)

Note that only type variables defined in global scope can be pickled.

# ion.units
Helper classes and functions facilitating dealing with various metrics
## EarthRadius
```python
EarthRadius(self, /, *args, **kwargs)
```
Earth Radius
## to_kb
```python
to_kb(byte_count: int) -> float
```
Converts bytes to kilobytes
# ion.url
Helper functions for operations on urls
## make_url
```python
make_url(url: str, params: dict) -> str
```

Converts base url and params into a url
Usage:
    >>> make_url('http://max.com/max', {'max': 1, 'what': 'no'})
    'http://max.com/max?max=1&what=no'

## query_to_dict
```python
query_to_dict(query_str: str) -> Dict[str, str]
```

Convert url query component to dictionary
Usage:
    >>> query_to_dict('?max=max&foo=bar')
    {'max': 'max', 'foo': 'bar'}
    >>> query_to_dict('?')
    {}

## query_to_str
```python
query_to_str(query_dict: Dict[str, Any]) -> str
```

Convert a key-value mapping to url query format (with query keys sorted)
Usage:
    >>> query_to_str({'max': 'max', 'foo': 'bar'})
    '?foo=bar&max=max'

## no_www
```python
no_www(url: str) -> str
```

Removes www. from the front of string if it's there
Usage:
    >>> no_www('max.com')
    'max.com'
    >>> no_www('www.max.com')
    'max.com'

## parse
```python
parse(url: str, components: Union[str, List[str], NoneType] = None, as_dict: bool = False)
```

Parses url and returns parsed url in requested format
Arguments:
    url: url to be parsed
Keyword arguments:
    components: how should the output be formatted (or which field to include in case of as_dict=True)
                Choose from: scheme, host, port, path, query, fragment
    as_dict: should the parsed url be returned as dictionary?
             If False it's going to be returned as string

## iurl
```python
iurl(url, query: Union[List[str], bool] = False)
```

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

## domain
```python
domain(url, level=2)
```

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

