#!/usr/bin/env python
"""usage: %prog [-qNb] paths [-s scripts] [-R requirements] [-P projects]

Generate python program launcher scripts which initialise sys.path with script
relative paths to their dependencies. If you move the dependencies and the
scripts to a new location then the scripts do not need to be regenerated.

Uses facilities from pyrun to discover the dependency paths.
"""

import sys, os, types
from textwrap import dedent

import logging
log = logging.getLogger(__name__)

pyrun = None
pkg_resources = None
have_win32_cli_exe = False

def ensure_pyrun():
    global pyrun
    if pyrun:
        return
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
    if pkg_resources:
        return
    try:
        pkg_resources = __import__('pkg_resources')
    except ImportError:
        log.critical(dedent('''\
            Failed to import setuptools:pkg_resources. Try using pyrun.py if
            you wish to avoid - or can not - arange for setuptools to be
            installed.'''))
        sys.exit(-1)

isdir = os.path.isdir
split = os.path.split
join = os.path.join
dirname = os.path.dirname
basename = os.path.basename
normpath = os.path.normpath
abspath = os.path.abspath
expanduser = os.path.expanduser
expandvars = os.path.expandvars


def absnormpath(path):
    return normpath(abspath(expandvars(expanduser(path))))

def relativepath(target, origin):
    """

    >>> relativepath('local/foo/bar', 'local/foo')
    'bar'

    >>> relativepath('local/foo', 'local/foo/bar')
    '../foo'

    >>> normpath(abspath(
    ... relativepath('unrelated/foo', 'local/foo/bar'))
    ... ).replace(join(os.getcwd(), ''), '', 1)
    'unrelated/foo'

    """

    absorigin = absnormpath(origin)
    abstarget = absnormpath(target)

    # strip the drive and root specifier, (Note: normpath coerces '/' to '\')
    OD, OP = os.path.splitdrive(absorigin)
    originlocal = absorigin.replace(join(OD, os.path.sep), '', 1)
    TD, TP = os.path.splitdrive(abstarget)
    targetlocal = abstarget.replace(join(TD, os.path.sep), '', 1)

    def numsegments(path):
        ctr = 0
        while path and not path.startswith(os.path.sep):
            path = dirname(path)
            ctr += 1
        return ctr

    if targetlocal.startswith(originlocal):
        # T              O
        # local/foo/bar, local/foo => bar
        if targetlocal == originlocal:
            return target
        return targetlocal.replace(join(originlocal, ''), '', 1)

    elif originlocal.startswith(targetlocal):
        # T              O
        # local/foo, local/foo/bar => ../foo
        relative = [os.path.pardir] * numsegments(
                originlocal.replace(join(targetlocal, ''), '', 1))
        remainder = originlocal.replace(targetlocal, '', 1)
        relative.append(basename(targetlocal))
        return join(*relative)
    else:

        cpr = os.path.commonprefix([targetlocal, originlocal])
        if cpr:
            relative = [os.path.pardir] * (
                    numsegments(originlocal.replace(cpr, '', 1))
                    #numsegments(originlocal) - numsegments(cpr)
                    )
            remainder = targetlocal.replace(cpr, '', 1)
            relative.append(remainder)
        else:
            # T              O
            # unrelated/foo, local/foo/bar => ../../../unrelated/foo
            # unrelated paths, relative segment is simply the address of the
            # local filesystem root
            relative = [os.path.pardir] * numsegments(originlocal)
            relative.append(targetlocal)
        return join(*relative)


def relativepaths(paths, origin):
    return (relativepath(p, origin) for p in paths)


def resolve_egg_scripts(path, reqs=None, projects=None, scriptnames=None):

    ensure_pkg_resources()

    if scriptnames is None:
        scriptnames = {}

    includescripts = frozenset([k for k,v in scriptnames.iteritems() if v])

    env = pkg_resources.Environment(path)
    ws = pkg_resources.WorkingSet([])
    if reqs is None:
        reqs = []
    if projects is not None:
        for p in projects:
            try:
                reqs.append(env[p][0].as_requirement())
            except KeyError:
                log.warning('Project "%" not found', p)


    # No explicit projects or requirements, assume the caller has organised
    # a useful collection of eggs under items in path and invent a list
    # of requirements based on the "best" distribution for each project
    # and any scripts witch the caller has requested.
    if not reqs:
        if scriptnames:
            # user has selected an explicit set of scriptst they want.
            for project in env:
                dist = env[project][0]
                emap = dist.get_entry_map()
                if set(emap.keys()).intersection(includescripts):
                    req = dist.as_requirement()
                    if req not in reqs:
                        reqs.append(req)
        else:
            # No explicit script selection, take them all
            reqs = [env[project][0].as_requirement() for project in env]
            print reqs


    reqs[:] = [
            pkg_resources.Requirement.parse(req)
                if isinstance(req, types.StringTypes) else req
            for req in reqs]
    # Collect all the scripts for all the resolved distributions. If we get
    # script name colisions, either as a result of or inspite of scriptrenames
    # via  scriptnames, log a warning and ignore the later definition.
    # While we are at it prune any scripts which have a 'False' entry in
    # scriptnames
    entrypoints = {}
    locations = []
    for dist in ws.resolve(reqs, env=env):
        dist.activate()
        print dist.location
        for name, ep in dist.get_entry_map('console_scripts').iteritems():
            sname = scriptnames.get(name, name)
            if sname is False:
                log.info('Ignoring "%s" from "%s", on request',
                        sname, dist.location)
                continue
            arguments = ''
            if sname is None: # dict.fromkeys does this to us
                sname = name
            if not isinstance(sname, types.StringTypes):
                if len(sname):
                    sname = sname[0]
                if len(sname) > 2:
                    arguments = sname[1]
            if sname in entrypoints:
                log.warning(
                dedent('''\
                Allready have "%s" from "%s", ignoring later definition from
                "%s"'''),
                sname, entrypoints[sname].dist.location, dist.location)

            entrypoints[sname] = (name, ep, arguments)
            if dist.location not in locations:
                locations.append(dist.location)

    script_parameters = []
    for sname, (name, ep, arguments) in entrypoints.iteritems():
        script_parameters.append((sname, name, ep.module_name,
            '.'.join(ep.attrs), arguments))

    return locations, script_parameters


_default_generator_opts=dict(
    dry_run=False,
    extrapath=(),
    executable=None, initialization='',
    arguments=None, template=None,
    xtemplatekw=None
    )

def generate_egg_scripts(path, reqs, projects, scripts, bindir, **kw):

    ensure_pkg_resources()
    variables = _default_generator_opts.copy()
    variables.update(kw)


    default_arguments = variables['arguments'] or ''

    if not isinstance(scripts, dict):
        scripts = dict.fromkeys(list(scripts))

    locations, parameters = resolve_egg_scripts(
            path, reqs, projects, scripts)
    generated = []
    for sname, name, module_name, attrs, arguments in parameters:
        # If we are simply given a path, generate *ALL* scripts,
        # Otherwise only generate those which are explicitly requested.

        # If an explicit set of scripts is specified only generate those
        # that are in the set.
        if scripts and name not in scripts:
            continue
        # if the original scripts argument was a flat list it is simply saying
        # "these are the scripts I want". If was a dict of some kind,
        # resolve_egg_scripts has incorporated any supported specializations
        # in its production of parameters.

        invoke_program = '%s.%s(%s)' % (module_name, attrs, arguments or
                    default_arguments)

        sname = join(bindir, sname)
        generated.extend(
            generate_script(module_name, locations, sname,
                invoke_program=invoke_program,
                **variables
                )
            )

    return generated


def generate_script(module_name, path, dest, **opts):
    """Generate script `dest` with bake in relative paths to items in `path`

    """
    ensure_pkg_resources()

    variables = _default_generator_opts.copy()
    variables.update(opts)

    dry_run = variables['dry_run']
    extrapath = variables['extrapath']
    executable = variables['executable']
    initialization = variables['initialization']
    arguments = variables['arguments']
    template = variables['template']
    xtemplatekw = variables['xtemplatekw']
    invoke_program = variables.get('invoke_program', None)

    if invoke_program is None:
        invoke_program = '%s.run(%s)' % (module_name, arguments or '')
    if not template:
        template = script_template
    if not executable:
        executable = sys.executable
    if initialization is None:
        initialization = ''
    if not xtemplatekw:
        xtemplatekw = {}

    generated = []

    path = list(relativepaths(path, dirname(dest)))
    if extrapath:
        path.extend(extrapath)

    path = ',\n    '.join([
        'pathentry("%s")' % p for p in path])

    script = dest
    if sys.platform == 'win32':
        dest += '-script.py'

    templatekw = dict(
        python = executable,
        path = path,
        module_name = module_name,
        initialization = initialization,
        invoke_program = invoke_program
        )
    templatekw.update(xtemplatekw)
    contents = template % templatekw

    changed = not (os.path.exists(dest)
            and open(dest).read() == contents)

    if sys.platform == 'win32':
        if not have_win32_cli_exe:
            log.warning(
            dedent("""\
            Unable to generate win32 executable wrapper as pkg_resources and
            its win32 cli.exe is not availabe; Hint: did you forget include a
            path to setuptools in your discovery path ?"""))
        else:
            # generate exe file and give the script a magic name:
            exe = script+'.exe'
            if not dry_run:
                open(exe, 'wb').write(
                    pkg_resources.resource_string('setuptools', 'cli.exe')
                    )
            generated.append(exe)

    if changed:
        if not dry_run:
            open(dest, 'w').write(contents)
        try:
            os.chmod(dest, 0755)
        except (AttributeError, os.error):
            pass
    generated.append(dest)
    return generated


script_template = '''\
#!%(python)s

from os.path import abspath, normpath, join, dirname, expanduser, expandvars
from os.path import isabs

def pathentry(path):
    path = expandvars(expanduser(path))
    if isabs(path):
        return path
    scriptdir = dirname(expandvars(expanduser(__file__)))
    return normpath(join(scriptdir, path))

import sys
sys.path[0:0] = [
    %(path)s
    ]
%(initialization)s

import %(module_name)s

if __name__ == '__main__':
    %(invoke_program)s
'''

#-----------------------------------------------------------------------------
# test facilities

def _mktest_paths(pathstring):
    return [p for p in dedent(pathstring).split('\n') if p]

def test_1():

    def checkresult(p, r, sn, c):
        print "(%s, %s => %s):\n   c == p ? %s" % (p, sn, r, c == p)
        return c == p, (
                '"%s" != "%s"' % (c, p))

    def absnormpath(*parts):
        return normpath(abspath(join(*parts)))

    def test(paths, scriptname):
        scriptdir = dirname(scriptname)
        print '*', scriptname
        print
        for i, relative in enumerate(relativepaths(
                paths, scriptdir)):
            assert checkresult(paths[i], relative, scriptname,
                absnormpath(scriptdir, relative))
        print

    paths=_mktest_paths("""\
        /aa/bb/cc/dd/libs1/file1
        /aa/bb/cc/dd/libs1/file2
        /aa/bb/cc/libs2/file3""")

    test(paths, '/aa/bb/cc/bin/script')

    test(paths, '/aa/bb/cc/script')

    test(paths, '/aa/bb/script')

def run_tests():
    import doctest; doctest.testmod()
    test_1()
    #print "'%%s/%s' %% (\n    dirname(normpath(abspath(__file__))))" % relative
    #print "'%%s/%s' %% SCRIPTDIR" % relative
    #print "normpath(abspath(join(SCRIPTDIR, '%s')))" % relative

#-----------------------------------------------------------------------------
# command line tool

def reportline(head, tail, truncate=78, reportmethod=log.info):

    if not truncate:
        reportmethod(''.join([head, tail]))
    else:
        maxlen = truncate - len(tail) - 1
        if len(head) > maxlen:
            maxlen -= len(' ...')
            reportmethod(head[:maxlen] + ' ... ' + tail)
        else:
            head += ' ' * (maxlen - len(head))
            reportmethod(''.join([head, tail]))


def get_options(parser=None):
    """Create (or update) an optparse.OptionParser.

    Defines the command line interface."""

    if parser is None:
        import optparse
        parser = optparse.OptionParser(usage=__doc__)

    parser.add_option('-q', '--quiet', default=False, action='store_true')
    parser.add_option('-N', '--dry-run', default=False, action='store_true')
    parser.add_option('-R', dest='requirements', default=[], action='append')
    parser.add_option('-P', dest='projects', default=[], action='append')
    parser.add_option('-s', dest='scripts', default=[], action='append')
    parser.add_option('-b', '--bindir', default='bin')

    return parser

def run(argv=None):

    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    log.setLevel(logging.INFO)


    ensure_pkg_resources()
    ensure_pyrun()

    parser = get_options()


    if argv is None:
        argv=sys.argv[:]

    parser.disable_interspersed_args()
    opts, args = parser.parse_args(args=argv[1:])

    dry_run = getattr(opts, 'dry_run', False)
    legal_postpath_opts={
            '-R': opts.requirements, '-P' : opts.projects, '-s':opts.scripts
            }


    logging.basicConfig(
            level=logging.DEBUG if not opts.quiet else logging.INFO,
            format='%(message)s'
            )

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

    if ia < len(argv):
        def opt_ileagal_after_discoverypath(opt):
            log.error(dedent('''\
                "%s" is ileagal after the discovery path. [%s] are the only
                options which may follow the discovery path.''' % (opt,
                    '|'.join(legal_postpath_opts.keys())))
                )

        if argv[ia] not in legal_postpath_opts:
            opt_ileagal_after_discoverypath(argv[ia])
            sys.exit(-1)
        curoplist = legal_postpath_opts[argv[ia]]
        ia += 1
        while ia < len(argv):
            if argv[ia] in legal_postpath_opts:
                curoplist = legal_postpath_opts[argv[ia]]
            elif argv[ia].startswith('-'):
                opt_ileagal_after_discoverypath(argv[ia])
                sys.exit(-1)
            else:
                curoplist.append(argv[ia])
            ia += 1

    generated = generate_egg_scripts(pthextend,
            opts.requirements,
            opts.projects,
            opts.scripts,
            opts.bindir,
            dry_run=dry_run)

    status='[ok]' if not dry_run else '[dry-run]'
    for sn in generated:
        reportline(sn, status)



if __name__=='__main__':
    run()
