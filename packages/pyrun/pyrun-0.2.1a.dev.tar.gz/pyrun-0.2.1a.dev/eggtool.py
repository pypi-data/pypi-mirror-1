#!/usr/bin/env python
"""usage: %prog [--list|--list-scripts] [discovery-path]

If this script is not installed simply invoke it like:
    `python eggtool.py`

To list distributions available on the discovery path:
    `eggtool [--list|-l] discovery-path`

To list projects and the console scripts they provide:
    `eggtool [--list-scripts|-L] discovery-path`

    The result is a list of project names followed by the entry points
    that project provides

To run a script provided by an egg package:
    `eggtool project discovery-path -s script script-command-line`


If `eggtool list disco/path1 disco/path2` shows:
    `foo:bar,baz`

Then use::
    eggtool foo disco/path1 disco/path2 -s bar
    eggtool foo disco/path1 disco/path2 -s baz

to run each of the scripts bar and baz.

"""

import os, sys, logging
from os.path import dirname, abspath, normpath, expanduser, join, commonprefix
from textwrap import dedent

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
pyrun = None
pkg_resources = None

def ensure_pyrun():
    global pyrun
    try:
        pyrun = __import__('pyrun')
    except ImportError:
        log.critical(dedent('''\
        Failed to import pyrun. Note that pyrun is a self contained python
        script and need not be installed to use. eggtool asumes you are using
        it to run eggtool.py (hence its available for import) or have made
        pyrun.py available on the PYTHONPATH using some other means.'''))
        sys.exit(-1)

def ensure_pkg_resources():
    global pkg_resources
    try:
        pkg_resources = __import__('pkg_resources')
    except ImportError:
        log.critical(dedent('''\
            Failed to import setuptools:pkg_resources. Try using pyrun.py if
            you wish to avoid - or can not - arange for setuptools to be
            installed.'''))
        sys.exit(-1)

#-----------------------------------------------------------------------------
# command line tool

def list_entry_points(opts, args):

    ensure_pyrun()
    ensure_pkg_resources()

    eggdirs = args

    group = getattr(opts, 'group', 'console_scripts')
    env = pkg_resources.Environment(eggdirs)
    for project in env:
        dist = env[project][0]
        entrypts = dist.get_entry_map(group).keys()
        if not entrypts:
            continue
        log.info('%s: %s', project, ','.join(entrypts))


def list_distributions(opts, args):
    ensure_pyrun()
    ensure_pkg_resources()
    eggdirs = args
    env = pkg_resources.Environment(eggdirs)
    for project in env:
        dist = env[project][0]
        log.info('%s => %s', project, dist.location)


def run_console_script(opts, project, eggpths, argv):
    ensure_pyrun()
    ensure_pkg_resources()


    env = pkg_resources.Environment(eggpths)
    ws = pkg_resources.WorkingSet([])

    ep = env[project][0].get_entry_map('console_scripts')[opts.script]
    #ep = env[project][0].get_entry_info('console_scripts', ep)
    sysargv = sys.argv[:]
    try:
        sys.argv = argv[:]
        for dist in ws.resolve([env[project][0].as_requirement()], env=env):
            dist.activate()
        ep.load(env=env)()
    finally:
        sys.argv[:] = sysargv[:]


def get_options(parser=None):
    """Create (or update) an optparse.OptionParser.

    Defines the command line interface."""

    if parser is None:
        import optparse
        parser = optparse.OptionParser(usage=__doc__)
    parser.add_option('-q', '--quiet', default=False, action='store_true')
    parser.add_option('-l', '--list', default=False, action='store_true')
    parser.add_option('-L', '--list-scripts',
            default=False, action='store_true')
    parser.add_option('-s', '--script')

    return parser

def run(argv=None):

    ensure_pyrun()
    ensure_pkg_resources()

    if argv is None:
        argv=sys.argv[:]

    parser = get_options()

    parser.disable_interspersed_args()

    default_opts = parser.defaults.copy()
    short_opts = {}
    for k,v in default_opts.items():
        opt = '--'+k.replace('_','-')
        o = parser.get_option(opt)
        for sopt in o._short_opts:
            short_opts[sopt[1:]] = k
        for lopt in o._long_opts:
            default_opts[lopt[2:].replace('-','_')] = v

    flag_opts = set([o.dest for o in parser.option_list
        if o.action in ('store_true', 'store_false')])

    opts, args = parser.parse_args(args=argv[1:])
    logging.basicConfig(
            level=logging.DEBUG if not opts.quiet else logging.INFO,
            format='%(message)s'
            )


    if not (opts.list or opts.list_scripts):
        project = args[0]
        del args[0]

    argv = args[:]
    pthextend, minfos, ia, doesnotexist = pyrun.discover_path(
            None, 0, *argv)

    if not opts.quiet and doesnotexist:
        log.warning(dedent('''\
        Warning: your discovery path arguments referenced the following
        files or directories which do not exist on the file system:
        ''')
        )
        log.warning('\t' + '\n\t'.join(doesnotexist))

    if opts.list:
        list_distributions(opts, pthextend)
    elif opts.list_scripts:
        list_entry_points(opts, pthextend)
    else:
        # If there are no unconsumed arguments: We have already determined
        # the user does not want to run a module. So we are done.
        inferior_argv = pyrun.get_inferior_argv(
                opts, default_opts, flag_opts, argv, ia, short_opts)
        run_console_script(opts, project, pthextend, inferior_argv)

if __name__ == '__main__':
    logging.basicConfig(format='%(message)s')
    run()

