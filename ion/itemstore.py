'''InYourArea ItemStore helper functions and classes'''
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import logging
import time

from .requests import Requests
from .url import parse, domain
from ._class import DCDict
from .time import msts
from .time.period import Period
from .hash import md5

log = logging.getLogger(__name__)
# id and iid scheme constants
# '76b79801-8d3e-4158-a280-afb2e505adf0'
ID_LEN = 36
ID_CHUNKS_NO = 5
ID_CHUNK_LENS = [8, 4, 4, 4, 12]


# TODO: List attributes
@dataclass
class Publisher(DCDict):
    '''
    ItemStore Publisher representing Harvester Publisher
    Attributes:
        ---
    '''
    name: str
    uuid: Optional[str] = None
    settings: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.uuid is None:
            self.uuid = md5(self.name)


@dataclass
class SimplifiedPublication(DCDict):
    '''ItemStore Simplified Publication representing Harvester Publication'''
    url: str
    publisher: Optional[str] = None
    mode: Optional[str] = 'smart'
    def expand(self):
        '''Convert simplified publication into a fill publication'''
        _domain = domain(self.url)
        section: Dict[str, Any] = {
            'url': self.url,
            'job': {
                'default': self.mode,
                'entrypoint': self.url
            }
        }
        return Publication(**{
            'name': _domain,
            'domain': _domain,
            'publisher': self.publisher,
            'sections': [
                section
            ]
        })


@dataclass
class Publication(DCDict):
    '''ItemStore Publication representing Harvester Publication'''
    name: str
    domain: str
    publisher: str
    sections: list
    uuid: Optional[str] = None
    config: dict = field(default_factory=dict)
    parent_iid: Optional[str] = None
    parent_type: Optional[str] = None
    iid: Optional[str] = None
    settings: dict = field(default_factory=dict)

    def __post_init__(self):
        self.domain = domain(self.domain)
        self.sections = [Section(**section) for section in self.sections]
        self.uuid = md5(self.domain)


# TODO: Consider removing settings from Section dataclass
@dataclass
class Section(DCDict):
    '''
    ItemStore Section representing Publication's section
    Attributes:
        name: Name of the section (can be None)
        url: url of the section consisting of only domain and slugs e.g. inyourarea.co.uk/news/ion-with-dataclasses
        uuid: md5 hashed url (used for de-duplication)
        job: job definition associated with the section
        settings: settings for this particular section
    '''
    url: str
    job: dict
    name: Optional[str] = None
    settings: dict = field(default_factory=dict)
    uuid: Optional[str] = None

    def __post_init__(self):
        self.url = domain(self.url, level=None) + parse(self.url, 'path query')
        if self.uuid is None:
            self.uuid = md5(self.url)


def is_valid_id(_id: str) -> bool:
    '''Checks whether itemstore id or iid is valid'''
    if not isinstance(_id, str):
        return False
    if len(_id) != ID_LEN:
        return False
    id_chunks = _id.split('-')
    if len(id_chunks) != ID_CHUNKS_NO:
        return False
    if [len(chunk) for chunk in id_chunks] != ID_CHUNK_LENS:
        return False
    return True

# TODO: Enable new Paginator flow
# Paginator()
#     .get('articles')
#     .params(
#         after=0
#         before=now()
#     )
#     .limit(100)
#     .map(
#         lambda item: item
#     )
#     .end()
class Paginator(object):
    MAX_BATCH_SIZE = 3000
    DEFAULT_BATCH_SIZE = 500

    def __init__(
            self,
            url,
            total_count: Optional[int] = None,
            batch_size: int = DEFAULT_BATCH_SIZE,
            period: Optional[str] = None,
            max_retries: int = 5,
            **kwargs
    ):
        requests = Requests()
        self.REQUEST_TYPES = {
            'GET': requests.get
        }
        self.requested_count = total_count
        self.batch_size = batch_size
        self.max_retries = max_retries
        self._request_type = 'GET'
        self.req = self.REQUEST_TYPES[self._request_type]
        self.url = parse(url, ['scheme', 'host', 'path'])
        self.last_batch = None
        self._batch = None
        self.returned = 0
        self.history = []
        params = parse(url, ['query'], as_dict=True)['query']
        params = dict(params or {}, **kwargs)
        self.params = params
        if period:
            if self.before or self.after:
                raise ValueError(f'period argument overrides other defined before or after')
            self.after = Period(period).to_timestamp(ms=True)
        self._init_params()
        log.info(
            "Initializing Paginator [%s] for '%s' with params: %r]",
            self._request_type,
            self.url,
            self.params
        )

    def _init_params(self):
        if self.after is None:
            self.after = 0
        if self.before is None:
            self.before = msts() + 1
        if self.count is None:
            self.count = self.batch_size

    @property
    def after(self):
        return self.params.get('after')

    @after.setter
    def after(self, value):
        self.params['after'] = value

    @property
    def before(self):
        return self.params.get('before')

    @before.setter
    def before(self, value):
        self.params['before'] = value

    @property
    def count(self):
        return self.params.get('count')

    @count.setter
    def count(self, value):
        self.params['count'] = value

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, value):
        self.last_batch = self._batch
        self._batch = value

    @property
    def clean_batch(self):
        if self.last_batch is None:
            return self.batch
        iids = set(item['iid'] for item in self.last_batch)
        return [item for item in self.batch if item['iid'] not in iids]

    def update_params(self):
        self.history.append(self.before)
        earliest_timestamp = min(item['lastModifiedTime'] for item in self.batch)
        latest_timestamp = max(item['lastModifiedTime'] for item in self.batch)
        if earliest_timestamp == latest_timestamp:
            if self.clean_batch:
                if self.count != self.MAX_BATCH_SIZE:
                    new_count = min(self.count * 2, self.MAX_BATCH_SIZE)
                    log.info(
                        ('Page is filled with items of the same lastModifiedTime, but page is not finished... '
                         'Increasing count param from %s to %s'),
                        self.count,
                        new_count
                    )
                    self.count = new_count
                else:
                    log.warning(
                        ('Encountered a page filled with %s items with the same timestamp %s!!! '
                         'Some items are going to be ignored...'),
                        len(self.batch),
                        earliest_timestamp
                    )
                    self.before = earliest_timestamp - 1
            else:
                log.info('Received empty batch - stopping...')
                raise StopIteration
        else:
            self.before = earliest_timestamp
            self.count = self.batch_size

    def issue_request(self):
        retries = 0
        while retries <= self.max_retries:
            response = self.req(self.url, params=self.params)
            if response.ok:
                return response.json()
            log.warning(
                'Retrying request %s to %s with params %s [%s]',
                self._request_type,
                self.url,
                self.params,
                response
            )
            time.sleep(2 ** retries)
            retries += 1
        log.error(
            'Too many retries %s for %s to %s with params %s [%s]',
            retries,
            self._request_type,
            self.url,
            self.params,
            response
        )
        raise StopIteration

    def __iter__(self):
        try:
            while self.after <= self.before:
                self.batch = self.issue_request()
                if self.batch:
                    for item in self.clean_batch:
                        yield item
                        self.returned += 1
                        if self.requested_count is not None and self.returned >= self.requested_count:
                            log.info(
                                'Requested count %s met - stopping...',
                                self.requested_count
                            )
                            raise StopIteration
                    self.update_params()
                else:
                    log.info('Received empty batch - stopping...')
                    raise StopIteration
            log.info('Reached end of specified period: %s', self.after)
        except StopIteration:
            return
