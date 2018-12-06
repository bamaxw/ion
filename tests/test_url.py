'''Testing ion.url'''
import unittest

from hypothesis import given
import hypothesis.strategies as st

from ion.url import parse, domain


DOMAIN_REGEX = r'^[a-zA-Z0-9][a-zA-Z0-9\.\-]*\.[a-zA-Z0-9\.\-]*(?<![\.\-])$'

domains = st.from_regex(DOMAIN_REGEX, fullmatch=True) # pylint: disable=invalid-name

class TestUrl(unittest.TestCase):
    '''Testing ion.url module'''
    @given(st.text())
    def test_parse_url_doesnt_fail(self, url):
        '''
        ion.url.parse should not fail for any input,
        but rather return None for a non-url
        '''
        try:
            parse(url)
        except Exception as ex: # pylint: disable=broad-except
            self.fail(f"ion.url.parse failed with error! {ex!r}")

    @given(domains)
    def test_domain(self, _domain):
        '''
        If a domain is passed as an argument to domain function
        and the requested level is None, it should return the original domain
        '''
        self.assertEqual(
            domain(_domain, level=None),
            _domain
        )
