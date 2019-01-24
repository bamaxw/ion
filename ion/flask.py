from typing import Callable, Optional, List
from functools import wraps, partial
import logging
import simplejson as json

import flask

from ion.dictionary import path
from ion.time import pts

log = logging.getLogger(__name__)
DEFAULT_HEADERS = {'Content-Type': 'application/json'}
HEADER_PRESETS = {
    'json': {
        'Content-Type': 'application/json'
    }
}


def with_payload(func: Optional[Callable] = None, *, named_argument='payload') -> Callable:
    '''
    A flask route function wrapper that passes
    request's json payload as named argument
    Arguments:
        named_argument -- use this to change the named argument as which
                          the payload is going to be passed to the wrapped function as
    '''
    if func is None:
        return partial(with_payload, named_argument=named_argument)
    @wraps(func)
    def _wrapper(*a, **kw):
        try:
            kw[named_argument] = flask.request.get_json(force=True)
        except:
            log.exception("Could not read POST body!")
            raise ClientError("Could not read POST body!")
        return func(*a, **kw)
    return _wrapper

def catch_api_error(func):
    '''
    Decorator function that takes a function as an argument
    and in case of any APIErrors being caught -> it returns its response
    '''
    @wraps(func)
    def _func(*a, **kw):
        try:
            return func(*a, **kw)
        except APIError as api_error:
            log.exception(func)
            return api_error.response
    return _func

def from_payload(*arglist):
    '''Decorator function that takes passes named arguments taken from request payload to the wrapped function'''
    def _decorator(func):
        @with_payload
        @wraps(func)
        def _wrapper(*a, payload, **kw):
            selected = get_args_from_payload(arglist, payload)
            return func(*a, **kw, **selected)
        return _wrapper
    return _decorator

def with_route(func):
    '''Decorator function passing flask route as a named argument'''
    @wraps(func)
    def _wrapper(*a, **kw):
        return func(*a, route=flask.request.url_rule, **kw)
    return _wrapper

def insert_elapsed(func):
    '''
    Decrator function inserting 'elapsed' key to response headers
    with a value being the time elapsed between
    the start and end of the wrapped function execusion
    '''
    @wraps(func)
    def _wrapper(*a, **kw):
        start = pts()
        return_val = func(*a, **kw)
        return_val.headers = dict(return_val.headers, elapsed=pts()-start)
        return return_val
    return _wrapper

# Responses
def Response( # pylint: disable=invalid-name
        content: str,
        *,
        status: int,
        headers: Optional[dict] = None,
        apply_headers: Optional[list] = None,
        force_json: bool = False
):
    '''
    A wrapper around flask.Response constructor facilitating easier use and implementing various default values
    Arguments:
        content       -- response content
        status        -- response status code (change default value by changing ion.flask.DEFAULT_STATUS)
        headers       -- response headers (change default value by changing ion.flask.DEFAULT_HEADERS)
        apply_headers -- additional predefined headers to be applied
                         (for instance header 'json' applies 'Content-Type': 'application/json')
                         it is possible to add additional presets by editing ion.flask.HEADER_PRESETS
    '''
    if headers is None:
        headers = dict(**DEFAULT_HEADERS)
    if apply_headers is None:
        apply_headers = []
    for header_type in apply_headers:
        headers = dict(headers, **HEADER_PRESETS[header_type])
    if not isinstance(content, str) or force_json: # Json stringify response if it isn't a string
        json_content = json.dumps(content)
    else:
        json_content = content
    return flask.Response(json_content, status=status, headers=headers)

def APIResponse( # pylint: disable=invalid-name
        message: Optional[str] = None,
        *,
        msg_type: str = 'success',
        status: int = 200,
        headers: Optional[dict] = None,
        **kw
):
    '''
    API response is a wrapper around flask.Response
    returning a json response with a 'type' and 'message' preset fields
    plus anything passed to this function as a named argument
    '''
    payload = {'type': msg_type, 'message': message}
    payload = dict(payload, **kw)
    return Response(payload, status=status, headers=headers)


# Errors
class APIError(Exception):
    '''
    Base Error class used as flask error response
    Any key-word arguments passed to the constructor of this method are going to be passed
    to APIResponse constructor
    Properties:
        response -- api response to be returned if this error surfaces
    '''
    def __init__(self, message, **kw):
        super().__init__(message)
        self.response = APIResponse(message, msg_type='error', **kw)

class ClientError(APIError):
    '''
    ClientError class is used to signal an error response to be returned
    because of client's fault
    '''
    def __init__(self, *a, status=400, **kw): # pylint: disable=useless-super-delegation
        super().__init__(*a, status=status, **kw)

class ServerError(APIError):
    '''
    ClientError class is used to signal an error response to be returned
    because of server's fault
    '''
    def __init__(self, *a, status=500, **kw): # pylint: disable=useless-super-delegation
        super().__init__(*a, status=status, **kw)


# Helpers
def get_args_from_payload(arglist: List[str], payload: dict):
    '''
    Get key values from payload dictionary
    '''
    args = {}
    missing = []
    for arg in arglist:
        try:
            if isinstance(arg, str):
                args[arg] = payload[arg]
            elif isinstance(arg, dict):
                key = list(arg.keys())[0]
                if isinstance(key, str):
                    args[key] = payload.get(key, arg[key])
                else:
                    args[key[-1]] = path(arg, payload, default=arg[key])
            else:
                args[arg[-1]] = path(arg, payload)
        except KeyError:
            missing.append(arg)
    if missing:
        msg = f'POST payload to {flask.request.url_rule} missing required {missing}!!!'
        log.error(msg)
        raise ClientError(msg)
    return args
