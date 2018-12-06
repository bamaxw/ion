'''NLP helper functions and classes'''
from typing import List
import logging
import re

from nltk.stem import SnowballStemmer
import spacy

from .typing import MaybeList
from . import string

CAMEL_CASE_REGEX = r'(?:(?:[A-Z]+|[a-z])[a-z]*)|\d+'
VAR_DELIMITERS = {
    '-', '_'
}
LANGS = {
    'en': 'english',
    'ru': 'russian',
    'it': 'italian',
    'esp': 'spanish'
}
STEMMERS = {}
SPACY_LANGS = {}
log = logging.getLogger(__name__)


def get_stemmer(lang: str) -> SnowballStemmer:
    '''Get a word stemmer for a particular language'''
    if lang not in STEMMERS:
        STEMMERS[lang] = SnowballStemmer(LANGS[lang])
    return STEMMERS[lang]

def get_spacy_nlp(lang: str):
    '''Get spaCy nlp for a given language'''
    if lang not in SPACY_LANGS:
        try:
            SPACY_LANGS[lang] = spacy.load(lang)
        except OSError:
            log.exception('Failed to load model `%s`', lang)
            spacy.cli.download(lang)
            SPACY_LANGS[lang] = spacy.load(lang)
    return SPACY_LANGS[lang]

def past_tense(text: str) -> str:
    '''
    Convert word to its past tense form
    Usage:
        >>> past_tense('compute')
        'computed'
        >>> past_tense('max out')
        'maxed out'
    '''
    _words = text.split(' ')
    if len(_words) > 2:
        raise TypeError(f"{text} doesn't look like a verb!")
    if _words[0][-1] == 'e':
        _words[0] += 'd'
    else:
        _words[0] += 'ed'
    return ' '.join(_words)

def singular(word: str, lang: str = 'en') -> str:
    '''Convert word to its singular form'''
    capital = [char.istitle() for char in word]
    return ''.join(
        char.upper() if capital else char
        for char, capital in zip(get_stemmer(lang).stem(word), capital)
    )

def plural(word: str) -> str:
    '''
    Convert a word to its plural form
    Usage:
        >>> plural('computer')
        'computers'
        >>> plural('max')
        'maxes'
    '''
    if word[-1] in {'s', 'x'}:
        return word + 'es'
    return word + 's'

def camel_case_to_words(camel_case_var: str) -> List[str]:
    '''
    Convert camel case word into a list of words
    Usage:
        >>> camel_case_to_words('whatIsGoingOn')
        ['what', 'Is', 'Going', 'On']
        >>> camel_case_to_words('whoEvenUsesCamelCase')
        ['who', 'Even', 'Uses', 'Camel', 'Case']
    '''
    return [
        match for match in re.findall(CAMEL_CASE_REGEX, camel_case_var)
    ]

def var_to_words(var: str) -> str:
    '''
    Convert variable name into words
    Usage:
        >>> var_to_words('ugc-posts')
        ['ugc', 'posts']
        >>> var_to_words('very_small_variable')
        ['very', 'small', 'variable']
        >>> var_to_words('verySmallVariable')
        ['very', 'small', 'variable']
    '''
    word_lists = [
        camel_case_to_words(word.strip())
        for word in string.split(var, delimiters=VAR_DELIMITERS)
    ]
    return [
        word
        for word_list in word_lists
        for word in word_list
    ]


def capitalize_each(_str: MaybeList[str]) -> str:
    '''
    Capitalize each word in list or string
    Usage:
        >>> capitalize_each(['max', 'codes', 'helpers'])
        ['Max', 'Codes', 'Helpers']
        >>> capitalize_each('et al acclaimed most cited researcher')
        ['Et', 'Al', 'Acclaimed', 'Most', 'Cited', 'Researcher']
    '''
    if string is list:
        split = _str
    else:
        split = [
            word.strip()
            for word in _str.split()
            if word.strip() != ''
        ]
    return [
        word.capitalize()
        for word in split
    ]

def ordinal(n: int) -> str:
    '''
    Converts integer into an ordinal string
    Usage:
        >>> ordinal(1)
        '1st'
        >>> ordinal(10)
        '10th'
    '''
    no_str = str(n)
    if no_str[-1] == '1':
        return no_str + 'st'
    if no_str[-1] == '2':
        return no_str + 'nd'
    if no_str[-1] == '3':
        return no_str + 'rd'
    return no_str + 'th'

def sentences(text: str, lang: str = 'en') -> List[str]:
    '''Splits string into sentences'''
    return (sent for sent in get_spacy_nlp(lang)(text).sents)

def words(text: str, lang: str = 'en', punct: bool = False) -> List[str]:
    '''Split string into words'''
    return (word.text for word in get_spacy_nlp(lang)(text) if (word.pos_ != 'PUNCT' or punct))

def tokens(text: str, lang: str = 'en') -> list:
    '''Split string into tokens'''
    return (token for token in get_spacy_nlp(lang)(text))

def ari(text: str):
    '''Calculate automated readability index of text'''
    text = text.strip()
    if not text:
        return None
    no_sents = len(list(sentences(text)))
    no_words = len(list(words(text, punct=False)))
    no_chars = len([1 for c in text if string.isalphanum(c)])
    return 4.71 * (no_chars / no_words) + 0.5 * (no_words / no_sents) - 21.43
