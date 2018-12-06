'''Helper functions for package setup'''
import logging
import re

from .files import read, get_dirname

log = logging.getLogger(__name__)

VERSION_REGEX = r'^\s*__version__\s*=\s*(\"|\')(?P<version>.*)\1'


def get_version(package_name=None, filename=None):
    '''Find __version__ in file'''
    if package_name is None and filename is None:
        package_name = get_dirname(last=True)
        log.warning('Setting package name to default: %s', package_name)
    version_file = filename or f'{package_name}/__init__.py'
    if log.isEnabledFor(logging.DEBUG):
        log.debug('Searching for version in %s', version_file)
    version_str = read(version_file)
    match = re.search(VERSION_REGEX, version_str, flags=re.M)
    if match is None:
        raise ValueError("No version number found!")
    return match['version']
