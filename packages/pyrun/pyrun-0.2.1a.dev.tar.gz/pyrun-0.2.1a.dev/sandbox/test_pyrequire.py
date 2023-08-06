import os
import types
import pyrequire
from cStringIO import StringIO

from os.path import abspath, join, dirname
from tempfile import mkdtemp
import pyrequire

def test_update_section_options():
    o = pyrequire.update_section_options([])
    assert not o
    options = {}
    o = pyrequire.update_section_options([], options)
    assert options is o
    o = pyrequire.update_section_options([
        ('sec1', 'o1', '1'),
        ('sec1', 'o2', '2'),
        ('sec2', 'o3', '3'),
        ('sec2', 'o3', '4'),
        ], options
        )
    assert 'sec1' in o and 'sec2' in o
    assert isinstance(o['sec1']['o1'], types.StringTypes)
    assert isinstance(o['sec1']['o2'], types.StringTypes)
    assert isinstance(o['sec2']['o3'], list)


def test_get_fallback_paths():
    fbk, consume_arg = pyrequire.get_fallback_paths([])
    assert not fbk
    fbk2, consume_arg = pyrequire.get_fallback_paths([], fbk)
    assert fbk2 is fbk
    fbk, consume_arg = pyrequire.get_fallback_paths(['-o'])
    assert not fbk
    fbk, consume_arg = pyrequire.get_fallback_paths(['--o'])
    assert not fbk
    fbk, consume_arg = pyrequire.get_fallback_paths(['='])
    assert not fbk
    fbk, consume_arg = pyrequire.get_fallback_paths([':='])
    assert not fbk
    fbk, consume_arg = pyrequire.get_fallback_paths([':'])
    assert not fbk
    fbk, consume_arg = pyrequire.get_fallback_paths(['.'])
    assert len(fbk) == 1 and abspath('.') == fbk[0]

    basedir = dirname(__file__)
    directory = object()
    # get_fallback_paths does not test paths contained in .pth files exist
    # - but it *does* exclude non existing argument paths.
    fmap={
        # foo:bar verifies get_fallback_paths properly splits the path
        # argument, if it performs a test for 'foo:bar' then it is broken.
        os.pathsep.join(['foo','bar']) : False,
        # get_fallback_paths MUST convert paths to absoloute form before
        # testing them.
        abspath('.') : directory,
        # test it deals with empty .pth files
        join(basedir, 'empty.pth') : '',
        join(basedir, 'nonewline.pth') : '/foo/bar',
        join(basedir, 'linesandcomments.pth') : '\n'.join([
                '/foo/bar',
                '#/bar/foo',
                '/baz/bar'
                ]),
        join(basedir, 'relative.pth') : '\n'.join([
                'foo/bar',
                '/bar/foo'
                ])
        }
    def openfile(fn):
        v = fmap.get(fn, False)
        if v is not False and v is not directory:
            return StringIO(v)
        else:
            raise IOError(
                    'IOError: [Errno 2] No such file or directory: ' + fn)
    def pathexists(path):
        return path in fmap

    fbk, consume_arg = pyrequire.get_fallback_paths(['foo'],
            openfile=openfile,
            pathexists=pathexists
            )
    assert not fbk

    fbk, consume_arg = pyrequire.get_fallback_paths([join(basedir, 'empty.pth')],
            openfile=openfile,
            pathexists=pathexists
            )
    assert not fbk
    fbk, consume_arg = pyrequire.get_fallback_paths([join(basedir, 'nonewline.pth')],
            openfile=openfile,
            pathexists=pathexists
            )
    assert fbk and fbk[0]==fmap[join(basedir, 'nonewline.pth')]
    tmpdir = mkdtemp('-pyrequire_test_all_get_fallback_paths')
    os.chdir(tmpdir)
    try:
        fbk, consume_arg = pyrequire.get_fallback_paths([join(basedir, 'linesandcomments.pth')],
                openfile=openfile,
                pathexists=pathexists
                )
        assert '/baz/bar' in fbk and '/foo/bar' in fbk
        assert '#/bar/foo' not in fbk
        assert len(fbk) == 2

        # verify all paths are considered only in there absolute form
        fbk, consume_arg = pyrequire.get_fallback_paths([join(basedir, 'relative.pth')],
                openfile=openfile,
                pathexists=pathexists
                )
        assert '/bar/foo' in fbk and join(basedir, 'foo/bar') in fbk
        assert len(fbk) == 2
    finally:
        os.chdir(basedir)
        os.rmdir(tmpdir)

