import os
from os.path import abspath, join, curdir, sep, commonprefix, pardir
import shutil
import hashlib
import logging

def relpath(path, start=curdir):
    """
    Returns the relative path from `start` to `path`.
    Function taken from Python 2.6.
    """
    if not path:
        raise ValueError("no path specified")

    start_list = abspath(start).split(sep)
    path_list = abspath(path).split(sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(commonprefix([start_list, path_list]))

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)

def get_hash_from_path(path, algorithm='md4'):
    """
    Returns the hash of the file `path`.
    The default algorithm is md4.
    """
    f = open(path)
    content = f.read()
    f.close()
    m = hashlib.new(algorithm)
    m.update(content)
    return m.hexdigest()

def copy_file(src, dst):
    """
    Copy `src` to `dst`.

    The parent directories for `dst` are created.

    To increase performance, this function will check if the file `dst`
    exists and compare the md4 hash of `src` and `dst`. The file will
    only be copied if the hashes differ.

    The md4 algorithm is used for performance reasons. It is very much
    faster than md5 or sha1 and good enough to compare file contents.
    """
    try:
        os.makedirs(os.path.dirname(dst))
    except OSError:
        pass

    if os.path.isfile(dst):
        src_hash = get_hash_from_path(src)
        dst_hash = get_hash_from_path(dst)
        if src_hash == dst_hash:
            return
    try:
        shutil.copy(src, dst)
    except IOError:
        pass

