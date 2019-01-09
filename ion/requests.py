'''Requests helper functions and classes'''
from functools import wraps
import logging
import time

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests import *

from ._import import get_caller_module
from .url import make_url, query_to_str

log = logging.getLogger(__name__)


def restart_on_connerr(func):
    '''
    Method decorator catches ConnectionError and resets object's 'session'
    Must be called on a method!
    '''
    @wraps(func)
    def _wrapper(self, *a, **kw):
        retries = 0
        while retries < 2:
            try:
                return func(self, *a, **kw)
            except ConnectionError:
                log.exception('Restarting on ConnectionError')
                self.reset_session()
                time.sleep(2 ** retries)
                retries += 1
        return func(self, *a, **kw)
    return _wrapper

def request_repr(request: dict) -> str:
    '''
    Take request and convert it to its string representation of form
    "<method>: <url>?<sorted_params>?<sorted_payload>"
    '''
    url_with_params = make_url(request['url'], request['params'])
    payload_repr = query_to_str(request['payload'])
    _repr = f"{request['method']}: {url_with_params}{payload_repr}"
    return _repr


class Requests:
    '''
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
    '''
    DEFAULT_STATUS_FORCELIST = frozenset((400, 403, 500, 502, 503, 504))
    def __init__(
            self,
            max_retries=5,
            retry_on=(),
            accept_on=(),
            raise_on_status=False
    ):
        retry_on = self.DEFAULT_STATUS_FORCELIST.union(set(retry_on))
        self.status_forcelist = frozenset(
            status_code
            for status_code in retry_on
            if status_code not in set(accept_on)
        )
        self._caller_module = get_caller_module()
        self.max_retries = max_retries
        self.raise_on_status = raise_on_status
        self.session = None
        self.reset_session()

    def reset_session(self):
        '''Resets self.session'''
        log.info('Setting/Resetting session for Requests called from module %s', self._caller_module)
        self.session = Session()
        retries = Retry(
            total=self.max_retries,
            connect=0,
            backoff_factor=1,
            status_forcelist=self.status_forcelist,
            raise_on_status=True
        )
        adapter = HTTPAdapter(pool_connections=50, pool_maxsize=100, max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    @restart_on_connerr
    def request(self, method: str, *a, **kw) -> Response:
        '''Generic request method that makes an appropriate request based on request type'''
        return self.session.request(method, *a, **kw)

    def get(self, *a, **kw):
        '''Alias for request('get')'''
        return self.request('get', *a, **kw)

    def head(self, *a, **kw):
        '''Alias for request('head')'''
        return self.request('head', *a, **kw)

    def delete(self, *a, **kw):
        '''Alias for request('delete')'''
        return self.request('delete', *a, **kw)

    def post(self, *a, **kw):
        '''Alias for request('post')'''
        return self.request('post', *a, **kw)

    def put(self, *a, **kw):
        '''Alias for request('put')'''
        return self.request('put', *a, **kw)
