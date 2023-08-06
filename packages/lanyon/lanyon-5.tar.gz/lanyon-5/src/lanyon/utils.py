import os
import shutil
import hashlib


def get_hash_from_path(path, algorithm='md4'):
    """
    Returns the hash of the file `path`.
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
