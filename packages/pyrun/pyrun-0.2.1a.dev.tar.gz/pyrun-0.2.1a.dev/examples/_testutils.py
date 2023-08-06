import os, sys
from os.path import join, isabs
from tempfile import mkdtemp
from distutils.dir_util import mkpath

def printitems(itr):
    for i in itr:
        print i

def printpaths(paths, strip=''):
    printitems([canonical_path(p, strip=strip)
        for p in paths]
        )

def canonical_path(path, strip=''):
    if isabs(path) and strip and not isabs(strip):
        raise ValueError(
        'Absoloute paths require absoloute *native* strip prefixes.'
        )
    if not isabs(path) and strip and isabs(strip):
        raise ValueError(
        'Relative paths require relative *native* strip prefixes.'
        )
    if strip and not strip.endswith(os.path.sep):
        if strip.endswith('/'):
            strip = strip[-1] + os.path.sep
        else:
            strip += os.path.sep
    if strip:
        path = path.replace(strip, '', 1)

    return '/'.join(path.split(os.path.sep))


def mktmpfiles(filepaths, prefix='', tmpdir=None):
    """Create a tree of temporary files and directories based on `filepaths`.

    Each item in spec must be a string specifying a file or directory to be
    created. Each item is assumed to use the POSIX directory separator. Items
    ending with `/` will produce directories. All other items will create empty
    *binary* mode files.  Existing files are over written and existing
    directories are ignored.

    All paths *must* be relative. Each is converted to *native* format and
    `os.path.join`ed onto the end of `tmpdir`. If tmpdir is None, the default,
    then a temporary directory is created for you using `tempfile.mkdtemp`.
    Otherwise `tmpdir` must be a native path.

    :Returns:
        (tmpdir, paths). The returned paths are all relative (to tmpdir) and
        are canonicalized to use the POSIX directory separator '/'. tmpdir is
        *not* normalized and is returned in *native* format.

    Example:

        >>> tmpdir, filepaths = mktmpfiles(('A/B/', 'B/F'), prefix='pyrun')
        >>> for p in filepaths:
        ...     print p
        A/B/
        B/F
        >>> assert os.path.isfile(join(tmpdir, *'B/F'.split('/')))
        >>> assert os.path.isdir(join(tmpdir, *'A/B'.split('/')))

    """
    if tmpdir is None:
        tmpdir = mkdtemp(prefix=prefix)

    created = []
    for p in filepaths:
        if not p:
            continue
        if p.startswith('/') or isabs(p):
            raise ValueError(
                'Absoloute paths in `filepaths` are unacceptable: "%s"' % p
                )
        splitp = p.split('/')
        if not splitp[-1] and not splitp[0]:
            continue
        nativedir = join(tmpdir, *splitp[:-1])
        mkpath(nativedir)
        if splitp[-1]:
            file(join(nativedir, splitp[-1]), mode='wb')
        created.append(p)

    return tmpdir, created

if __name__ == '__main__':
    import doctest; doctest.testmod()
