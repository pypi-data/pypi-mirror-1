
pyrun.discover_and_run, pyrun.discover_path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the command line programs provided by this package are essentially thin
wrappers around the `discover_and_run` or `discover_path` functions. This
section provides `doctest` based discussion and examples. These examples are
also part of the pyrun test suite.

Lets setup a fake set of python packages and use it to illustrate some basics.

    >>> import os, sys
    >>> from os.path import join
    >>> import pyrun
    >>> from _testutils import mktmpfiles, printpaths
    >>> sysver_cur = sys.version[:3]
    >>> sysver_notcompatible = '.'.join(map(str,
    ...   [sys.version_info[0], sys.version_info[1] + 1]))
    >>> tmpdir, canonicalpaths = mktmpfiles((
    ...     'A/AA/paaa/__init__.py',
    ...     'A/AA/paaa/paaaa/',
    ...     'B/BB/paaa/__init__.py',
    ...     'B/BB/paaa/paaaa/',
    ...     'B/BB/pbbb/pbbbb/__init__.py',
    ...     'B/pc/__init__.py',
    ...     'Modules/module_a.py',
    ...     'Modules/module_b.py'),
    ...
    ...     prefix='pyrun-'
    ...     )


This search gives an os dependent ordering of all packages under A and B
lexicaly ordered depth first is common. Note that Modules is ignored.

    >>> pth, minfos, ia = pyrun.discover_and_run(['pyrun', tmpdir], run_module=False)
    >>> printpaths(pth, strip=tmpdir)
    A/AA
    B
    B/BB
    B/BB/pbbb

This search forces paths under 'B' to be considered first, again note that
Modules is ignored.

    >>> pth, minfos, ia = pyrun.discover_and_run(['pyrun',
    ...     join(tmpdir, 'B'), tmpdir], run_module=False
    ...     )
    >>> printpaths(pth, strip=tmpdir)
    B
    B/BB
    B/BB/pbbb
    A/AA

Modules is not present in either of the above resulting paths because python
module files are ignored unless they were explicitly mentioned in the search.

    >>> pth, minfos, ia = pyrun.discover_and_run(['pyrun', tmpdir,
    ...     join(tmpdir, 'Modules', 'module_a.py')], run_module=False)
    >>> printpaths(pth, strip=tmpdir)
    Modules
    A/AA
    B
    B/BB
    B/BB/pbbb

This search mentions two module files explicitly, in addition to the root
of our fake tree.

    >>> pth, minfos, ia = pyrun.discover_and_run(['pyrun', tmpdir,
    ...     join(tmpdir, 'Modules', 'module_a.py'),
    ...     join(tmpdir, 'Modules', 'module_b.py')], run_module=False)
    >>> printpaths(pth, strip=tmpdir)
    Modules
    A/AA
    B
    B/BB
    B/BB/pbbb

The discovery algorithm currently forces paths discovered from module files
ahead of those discovered for package files, however the paths for module
files still follow the order in which the module files are listed in the
search path.  Note that for module files which are contained in one directory
you only need to include one in the search but including many from the same
directory does not cause duplicates.
More elaborate schemes for addressing the shadowning problem are definitely
viable, especially given the module loading facilities in the runpy standard
lib module. I suspect the "force to front" rule is essential for covering
*my* use case which is "just fix my path and run that script damit!"


Lets drop some eggs into the mix. We dont use real eggs for these examples
because the discovery of eggs does not look at egg contents - only file and
directory names.

    >>> tmpdir, canonicalpaths = mktmpfiles((
    ...     'Modules/foo-0.1-py%s.egg' % sysver_cur,
    ...     'Modules/foo-0.2-py%s.egg' % sysver_cur,
    ...     'Modules/foo-0.2-py%s.egg-link' % sysver_cur,
    ...     'Modules/zzz-0.2-py%s.egg-link' % sysver_cur,
    ...     'Modules/foo-0.3-py%s.egg' % sysver_notcompatible,
    ...     'A/bar-0.1-py%s.egg' % sysver_cur,
    ...     'B/bar-0.2-py%s.egg' % sysver_cur),
    ...     tmpdir=tmpdir
    ...     )


A full search,

    >>> pth, minfos, ia = pyrun.discover_and_run(['pyrun', tmpdir], run_module=False)
    >>> printpaths(pth, strip=tmpdir)
    A/AA
    B/bar-0.2-py2.5.egg
    B
    B/BB
    B/BB/pbbb
    Modules/foo-0.2-py2.5.egg

A search that considers 'B' first

    >>> pth, minfos, ia = pyrun.discover_and_run(['pyrun',
    ...     join(tmpdir, 'B'), tmpdir], run_module=False
    ...     )
    >>> printpaths(pth, strip=tmpdir)
    B/bar-0.2-py2.5.egg
    B
    B/BB
    B/BB/pbbb
    A/AA
    Modules/foo-0.2-py2.5.egg

Note that irrespective which order we visit the A and B sub trees, we always
list bar-0.2. The search discards duplicate egg names, retaining the first
and - irispective of the visit order - *always* lists the best version of
each egg.

Finaly note that foo-0.3 is *not* listed. This is not a bug - the search
ignores eggs whose major & minor revisions dont match the current
interpreter. But, for now, no special care is taken to deal with platform
specific eggs (linux-i686 vs whatver windows eggs use.)


