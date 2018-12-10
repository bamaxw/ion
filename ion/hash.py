'''Helper functions and classes for hashing'''
from functools import partial
from typing import Any
import logging
import hashlib
import os

log = logging.getLogger(__name__)
_BUFFER_SIZE = 65536 # Magic number: 64kb
_HASHLIB_TYPES = {
    'sha1': hashlib.sha1,
    'md5': hashlib.md5
}

def genhash(string: Any, hashfunc, asbytes=False) -> str:
    '''Simplified hashlib hashing'''
    try:
        hashval = hashfunc(string)
    except TypeError:
        try:
            hashval = hashfunc(string.encode('utf-8'))
        except AttributeError:
            hashval = hashfunc(str(string).encode('utf-8'))
    if asbytes:
        hashval.digest()
    return hashval.hexdigest()


def hashfile(filepath: str, hash_object, buffer_size: int = _BUFFER_SIZE, asbytes=False) -> str:
    '''
    Hash contents of a file
    Arguments:
        filepath:    path to a file which contents are going to be hashed
        hash_object: hash object implementing .update() method [e.g. hashlib.sha1()]
        buffer_size: arbitrary buffer size to use for buffering file
    '''
    with open(filepath, 'rb') as file:
        while True:
            block = file.read(buffer_size)
            if not block:
                break
            hash_object.update(block)
    if asbytes:
        return hash_object.digest()
    return hash_object.hexdigest()

md5 = partial(genhash, hashfunc=hashlib.md5)

sha1 = partial(genhash, hashfunc=hashlib.sha1)

sha1file = partial(hashfile, hash_object=hashlib.sha1())

md5file = partial(hashfile, hash_object=hashlib.md5())

_ION_HASH_TYPES = {
    'sha1': sha1file,
    'md5': md5file
}

def hash_dir(dirpath: str, hash_type: str, recursive=True, asbytes=False):
    '''
    Hash contents of a directory
    Arguments:
        dirpath: path to a directory
        hash_type: name a of a hash to be used [e.g. 'sha1']
        recursive: should the hash be calculated recursively
    '''
    log.debug('[%s] Hashing directory %s', hash_type, dirpath)
    _, dirs, files = next(iter(os.walk(dirpath)))
    try:
        hash_object = _HASHLIB_TYPES[hash_type]()
        hash_func = _ION_HASH_TYPES[hash_type]
    except KeyError:
        raise ValueError(f"Can't hash directory with an invalid hash '{hash_type}'")
    for file in sorted(files):
        filehash = hash_func(
            os.path.join(dirpath, file),
            asbytes=True
        )
        log.debug('[f] %s <- %s', filehash, file)
        hash_object.update(filehash)
    for _dir in sorted(dirs):
        dirhash = hash_dir(
            dirpath=os.path.join(dirpath, _dir),
            hash_type=hash_type,
            recursive=recursive,
            asbytes=True
        )
        log.debug('[d] %s <- %s', dirhash, _dir)
        hash_object.update(dirhash)
    if asbytes:
        hash_object.digest()
    return hash_object.hexdigest()
