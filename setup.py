from setuptools import setup, find_packages
import os
import re


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), "rt") as fh:
        return fh.read()

_version_regex = r'^\s*__version__\s*=\s*(\"|\')(?P<version>.*)\1'
def get_version():
    version_str = read("ion/__init__.py")
    match = re.search(_version_regex, version_str)
    if match is None:
        raise ValueError("Failed to find version number")
    return match['version']

setup(
    name="ion",
    author="Maximus Wasylow",
    version=get_version(),
    author_email="bamwasylow@gmail.com",
    description="Python support package containing various utility and helper functions and classes grouped by theme",
    long_description=read("README.md"),
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'requests',
        'simplejson',
        'pytz',
        'pprint'
    ]
)
