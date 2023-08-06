#!/usr/bin/env python
import sys, os, doctest
from os.path import abspath, dirname, normpath, join

import os, sys, types
from os.path import isdir, isfile, dirname, abspath, join
from os.path import normpath

def get_info(data):
    RE_HEADER_KEY=(
    r'(?ims)^:?(?P<key>[a-z][\w\-_ ]*):\s*'
         '(?P<value>.*?'
         '(?=(\Z|\n^:?[a-z][\w\-_ ]*:)))'
         )
 
    import re
    info={}
    for k,v,_ in re.findall(RE_HEADER_KEY, data):
        info.setdefault(k,[]).append(v.strip())
    return info

try:
    from setuptools import setup
    HAVE_SETUPTOOLS = True
except ImportError:
    HAVE_SETUPTOOLS = False
    from distutils.core import setup

abs_pkg_info = join(dirname(abspath(__file__)), 'pkg-info.rst')

PKG_INFO=get_info(file(abs_pkg_info).read())

def update_docs(glob_pattern, ignore=None, docutils_conf=None):
    ignore = ignore or {}
    try:
        from docutils.core import publish_cmdline
    except ImportError:
        print 'failed to update docs, docutils not installed'
        return
    from glob import glob
    if docutils_conf:
        base_argv = ['--config=%s' % docutils_conf]
    else:
        base_argv = []
    for source in glob(glob_pattern):
        if source in ignore:
            continue
        dest = os.path.splitext(source)[0] + '.html'
        if not os.path.exists(dest) or \
               os.path.getmtime(dest) < os.path.getmtime(source):
            print 'building documentation file %s' % dest
            publish_cmdline(writer_name='html',
                            argv=base_argv + [source, dest])

update_docs('*.rst', ignore=['pkg-info.rst'])

setupkw=dict(
    name=PKG_INFO['Name'][0],
    version=PKG_INFO['Version'][0],
    description=PKG_INFO['Abstract'][0],
    long_description=file('README.txt').read(),
    author=PKG_INFO['Author'][0],
    license = PKG_INFO['License'][0],
    author_email = PKG_INFO['Author-email'],
    url = PKG_INFO['URL'][0],
    download_url = PKG_INFO['Download-URL'][0],
    py_modules=['pyrun'],
    package_dir = {'':'.'},
    classifiers=PKG_INFO['Classifiers'],
)
if HAVE_SETUPTOOLS:
    setupkw.update(
        entry_points = {
            'console_scripts': [
                'pyrun = pyrun:runex',
                'pyrunscripts = pyrunscripts:run',
                'eggtool = eggtool:run'
                ]
            },
        # Force unzip because pyrun is used to *discover* eggs and use them
        # without installing, or in cases where the setuptools easy-install.pth
        # machinery has been borked. To pyrun a python egg is no more than a
        # distribution format.
        zip_safe=False
    )
setup(**setupkw)

