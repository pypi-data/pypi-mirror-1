#!/usr/bin/python2.5
import os, sys
from glob import glob
from zipfile import is_zipfile
from os.path import *

def abs_normpath(path, *parts):
    if parts:
        return normpath(
                join(abspath(expanduser(path)), expanduser(join(*parts)))
                )
    else:
        return normpath(
            join(abspath(expanduser(path)))
            )

def relative_read(filename, *rnames):
    return open(abs_normpath(filename, *rnames)).read()

_="""alt rval
    If the import is successful return the 2 tuple, (abs_path, moduleinstance)
    The value of abs_path is determined cognizant of the actual import path as
    follows:

    * If successful **and its an ordinary file** based installation; abs_path
      is the absolute path to the directory containing TOP LEVEL module file.

    * If successful **and its an unzipped egg** based installation; abs_path is
      the absolute path to the egg directory.

    * If successful **and its a zipped egg** based installation; abs_path is
      the absolute path of the egg file.
"""

def loginfo(s, *a):
    print >> sys.stdout, s % a

from runpy import get_loader, _get_filename, _run_module_code

def get_module_code(mod_name):
    """like runpy.run_module but dont run."""
    loader = get_loader(mod_name)
    if loader is None:
        raise ImportError("No module named " + mod_name)
    code = loader.get_code(mod_name)
    if code is None:
        raise ImportError("No code object available for " + mod_name)
    filename = _get_filename(loader, mod_name)
    return filename, code, loader

def addsitepaths(pthfile, loginfo=loginfo):
    fn = abs_normpath(pthfile)
    for ln in file(fn):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        loginfo('Adding sitedir: %s' % ln)
        site.addsitedir(ln)

def _path_adder(add_path, added, p, e=None, loginfo=loginfo):
    if e is None:
        save_path = (p, sys.path[:])
        loginfo and loginfo('Adding path: %s' % p)
        add_path(p)
        added.add(p)
        return save_path
    else:
        p, save_path = p
        loginfo and loginfo('Undoing add path: %s' % p)
        added.remove(p)
        sys.path[:] = save_path[:]


def pth_import(modulename, fallback_paths,
        code_getter=get_module_code, path_adder=None,
        projectversion=False, pth_filename='pyrun.pth', loginfo=loginfo):
    """Attempt to obtain the module code for modulename.

    The following heuristic is used to attempt the import from a variety of
    fallback locations **if the initial get fails**:

    If any step is successful break out immediately and compute the
    return path.

    1. Make the first attempt without modifying the path.

    2. If pth_filename file exists in fallback_paths[0] then extend the
    path, via ``site.addsitedir`` with the directories listed in that file.

    3. Attempt again.

    4. If the import failed AND projectversion is not False, contstruct a glob
    pattern like this::
        ``abs_normpath(fallback_paths[0], projectversion+'-py'+sys.version[:3]+'*.egg')``
    and sort the results **in lexically ascending order**. If the result is non
    empty add it to the path and try again

    repeat 2., 3., 4. for every remaining path in fallback_paths

    """
    if not path_adder:
        import site
        # don't want to muck around with site._init_pathinfo and known_paths
        added = set([])
        def path_adder(p, e=None):
            return _path_adder(site.addsitedir, added, p, e=e, loginfo=loginfo)

    try:
        modcode = code_getter(modulename)
        return modcode
    except ImportError:
        pass
    for p in fallback_paths:
        if is_zipfile(p) or isdir(p):
            adder_key = path_adder(p)
        try:
            modcode = code_getter(modulename)
            return modcode
        except ImportError, e:
            path_adder(adder_key, e)
            if not projectversion and isdir(p):
                continue
        # glob patterns only apply when a projectversion is supplied and
        # the fallback path is a directory.
        pattern = abs_normpath(p, projectversion+'-py'+sys.version[:3]+'*.egg')
        loginfo and loginfo('egg glob pattern: %s', pattern)
        eggs = glob(pattern)
        if not eggs:
            continue
        eggs.sort()
        adder_key = path_adder(eggs[-1])
        try:
            modcode = code_getter(modulename)
            return modcode
        except ImportError, e:
            path_adder(adder_key, e)
            continue
    raise ImportError('No module named '+modulename)


if sys.platform == 'win32':
    # work around spawn lamosity on windows
    # XXX need safe quoting (see the subproces.list2cmdline) and test
    def _safe_arg(arg):
        return '"%s"' % arg
else:
    _safe_arg = str


def _error(message, *args):
    print >> sys.stderr, message % args
    sys.exit(-1)

_usage="""\
%(prog)s paths [-vqD] [-G [options-global]] [-R project[/version]]* \
    [--help] | [--section:option=value]+
"""
def _help():
    print _usage % dict(
            prog = splitext(basename(__file__))[0]
            )
    sys.exit(0)

def process_args(args=None):
    if args is None:
        args = sys.argv[:]
    run_name='__main__'
    verbosity = 0
    debug = False
    command = False
    modulename = False
    optionglobals = False
    options=[]
    projectversions = []
    while args:
        if args[0][0] == '-':
            op = orig_op = args.pop(0)
            op = op[1:]
            while op and op[0] in 'vqnDGR':
                if op[0] == 'R':
                    v = args.pop(0)
                    assert (not v.startswith('-') and len(v.split('/')) <= 2), (
                            '-R without a value or with illegal syntax, Try '
                            '"-R project/version" or just "-R project"'
                            )
                    projectversions.append(v)
                elif op[0] == 'n':
                    run_name = args.pop(0)
                    assert (not run_name.startswith('-')), (
                            '-n without a value, Try -n __main__ '
                            ' or -n myprogname '
                            )
                elif op[0] == 'v':
                    verbosity += 10
                elif op[0] == 'q':
                    verbosity -= 10
                elif op[0] == 'D':
                    debug = True
                elif op[0] == 'G':
                    if (args and not args[0].startswith('-') and not '=' in
                            args[0]):
                        optionglobals = args.pop(0)
                    else:
                        optionglobals = True
                else:
                    _help()
                op = op[1:]
            if op[:1] == 'c':
                op = op[1:]
                if op:
                    command = op
                else:
                    if args:
                        command = args.pop(0)
                    else:
                        _error(
                        "-c must be accompanied by a string to exec:orig_op='%s'", orig_op)
                break
            elif op[:1] == 'm':
                op = op[1:]
                if op:
                    modulename = op
                else:
                    if args:
                        modulename = args.pop(0)
                    else:
                        _error(
                        "-m must be accompanied by a module name to exec:orig_op='%s'", orig_op)
                break
            elif op:
                if orig_op == '--help':
                    _help()
                _error("Invalid option:%s", op)
        elif '=' in args[0]:
            option, value = args.pop(0).split('=', 1)
            if len(option.split(':')) != 2:
                _error('Invalid option:', option)
            section, option = option.split(':')
            options.append((section.strip(), option.strip(), value.strip()))
        else:
            # We've run out of command-line options and option assignments
            # The rest should be commands, so we'll stop here
            break

    return dict(verbosity=verbosity, debug=debug, optionglobals=optionglobals,
            command=command, modulename=modulename,
            run_name=run_name, options=options, args=args,
            projectversions=projectversions
            )

def parse_projectversion(pv, defaultver='*', logfn=False):
    pv = pv.split('/',1)
    if len(pv)==2 and pv[1]:
        proj, ver = pv[1]
    else:
        proj, ver = pv[0],'*'
    if ':' in proj:
        proj, modname = proj.split(':',1)
    else:
        modname=proj.lower().replace('-','_')
        modname='_'.join(modname.split())
        if modname != proj:
            logfn and logfn('Coerced project name from "%s" => "%s"', proj, modname)
    projver = '-'.join([proj, ver])
    return projver, proj, ver, modname


def update_section_options(sectionoptlist, options=None):
    if options is None:
        options = {}
    for s,so,v in sectionoptlist:
        s = options.setdefault(s, {})
        if so in s:
            if isinstance(s[so], list):
                s[so].append(v)
            else:
                s[so] = [s[so], v]
        else:
            s[so] = v
    return options


def get_fallback_paths(args, fallback_paths=None,
        openfile=file, pathexists=exists):
    consume_arg = False
    if fallback_paths is None:
        fallback_paths=[]
    if args and not args[0].startswith('-') and not '=' in args[0]:
        pth = args[0]
        consume_arg = True
        for p in pth.split(os.pathsep):
            if p.endswith('.pth'):
                p = abs_normpath(p)
                pth_file_dir = dirname(p)
                for ln in openfile(p):
                    ln = ln.strip()
                    if ln and not ln.startswith('#'):
                        fallback_paths.append(abs_normpath(pth_file_dir, ln))
            elif pathexists(p):
                fallback_paths.append(abs_normpath(p))
    return fallback_paths, consume_arg


def load_pvm_code(project_versions, fallback_paths,
    code_getter=get_module_code, path_adder=None,
    pvparsedpv=None, pymod=None, modcode=None, logfn=None):
    """Attempt to load the code for each project/version in project_versions.


    If at any time we get an ImportError from the `code_getter` we add
    successive items from fallback_paths using `path_adder` until we run out
    of paths or the `code_getter` is successful.

    The subject module name defaults to a safe interpretation of `project`.

    Does NOT execute module code if an appropriate ``code_getter`` is supplied.

    Supported syntax:
        ``project, project/``:
            project at 'best' version, module name is inferred.
        ``project/version``:
            project at a particular version, module name is inferred.
        ``project:module``:
            project at 'best' version, module name is explicit.
        ``project:module/version:
            project at a particular version with and explicit module name.
    """

    if fallback_paths is None:
        fallback_paths = []
    else:
        fallback_paths = list(fallback_paths)
    if pvparsedpv is None:
        pvparsedpv = {}
    if pymod is None:
        pvmod = {}
    if modcode is None:
        modcode = {}
    for pv in project_versions:
        if pv in pvmod:
            logfn('WARNING: redundant project version specifier: %s', pv)
            continue
        project_version, proj, ver, modname = parse_projectversion(
                pv, logfn=logfn)
        filename, code, loader = pth_import(
                modname, fallback_paths, projectversion=project_version,
                code_getter=code_getter, path_adder=path_adder,
                loginfo=logfn
                )
        # First wins
        pvparsedpv[pv] = (project_version, proj, ver, modname)
        pvmod[pv] = modname
        modcode[modname] = (filename, code, loader)
    return pvparsedpv, pvmod, modcode


PATHS_ADDED_MSG='''\
The paths whose addition enabled the import of at least
one of the requested modules or requirements - listed in the
order in which they were ADDED:'''
PATHS_IMPLICITLY_ADDED_MSG='''\
The following paths were implicitly added by the process
of satisfying the requested requirement - in a manner that
pyrun was unable to track. This is usually benign. Using
just the paths reported as `added` by pyrun (above) should
be enough to let you use the requirements and modules
directly. Paths IMPLICITLY ADDED:'''

def main2(args=None):
    if args is None:
        del sys.argv[0]
        args=sys.argv[:]

    fallback_paths, consume_arg = get_fallback_paths(args)
    if consume_arg:
        args.pop(0)

    o = process_args(args)

    project_versions = o['projectversions']
    globaloptions = o['optionglobals']
    section_options = o.get('options', [])
    modulename = o.get('modulename', False)
    run_name = o['run_name']
    py_statements = o['command']

    if 50 - o['verbosity'] < 21:
        logfn = loginfo
    else:
        logfn = lambda *a:None
    try:
        save_sys_path=sys.path[:]
        options = update_section_options(section_options)

        # Make the options available globaly ?
        ns={'__pyrun_options__':options}
        if not globaloptions:
            # still available globaly, just decorated
            pass
        elif globaloptions is True:
            ns.update(options)
        else:
            ns.update({globaloptions:options})

        class path_added(set):
            add_order = []
            def add(self, v):
                super(path_added, self).add(v)
                self.add_order.append(v)
        added = path_added()


        def path_adder(p, e=None):
            return _path_adder(sys.path.append, added, p, e=e, loginfo=logfn)

        import site
        def path_adder(p, e=None):
            return _path_adder(site.addsitedir, added, p, e=e, loginfo=logfn)

        pvparsedpv, pvmod, modcode = load_pvm_code(
                project_versions, fallback_paths,
                path_adder=path_adder
                )

        logfn(' '.join(sys.argv))
        if modulename is not False:
            sys.argv[:] = [modulename] + args
            if modulename in modcode:
                filename, code, loader = modcode[modulename]
            else:
                filename, code, loader = pth_import(
                        modulename, fallback_paths
                        )
                modcode[modulename] = (filename, code, loader)
            return _run_module_code(code, ns, run_name,
                            filename, loader, True)
        elif py_statements:
            sys.argv[:]=args
            sys.argv[:]=['-c'] + args
            logfn(' '.join(sys.argv))
            exec py_statements in ns
        elif isfile(args and args[0]):
            filename = args[0]
            sys.argv[:]=args
            execfile(filename, ns)
        else:

            logfn and logfn(PATHS_ADDED_MSG)

            print '\n'.join([p for p in added.add_order if p in added])
            if logfn:
                added_to_sys_path = set(sys.path) - set(save_sys_path)
                if added != added_to_sys_path:
                    logfn(PATHS_IMPLICITLY_ADDED_MSG)
                    print
                    print '# implicitly added'
                    print '\n'.join(list(set(sys.path) - set(save_sys_path)))

    except SystemExit:
        raise
    except Exception:
        if o['debug']:
            exc_info = sys.exc_info()
            import pdb, traceback
            traceback.print_exception(*exc_info)
            sys.stderr.write('\nStarting pdb:\n')
            pdb.post_mortem(exc_info[2])
        else:
            raise


def main(args=None):
    if args is None:
        del sys.argv[0]
        args=sys.argv[:]

    fallback_paths=[]
    if args and not args[0].startswith('-') and not '=' in args[0]:
        pth = args.pop(0)
        fallback_paths = []
        for p in pth.split(os.pathsep):
            if p.endswith('.pth'):
                fallback_paths.extend([ln.strip()
                        for ln in file(abs_normpath(p))
                        if ln.strip()
                        ])
            elif exists(p):
                fallback_paths.append(abs_normpath(p))

    o = process_args(args)

    if 50 - o['verbosity'] < 21:
        logfn = loginfo
    else:
        logfn = lambda *a:None
    try:
        sectionoptlist = o.get('options', [])
        options = {}
        for s,so,v in sectionoptlist:
            s = options.setdefault(s, {})
            if so in s:
                if isinstance(s[so], list):
                    s[so].append(v)
                else:
                    s[so] = [s[so], v]
            else:
                s[so] = v

        # Make the options available globaly ?
        globaloptions = o['optionglobals']
        ns={'__pyrun_options__':options}
        if not globaloptions:
            # still available globaly, just decorated
            pass
        elif globaloptions is True:
            ns.update(options)
        else:
            ns.update({globaloptions:options})

        pvmod = {}
        modcode = {}
        args = o['args']
        projvers = o['projectversions']
        for pv in projvers:
            if pv in pvmod:
                logfn('WARNING: redundant project version specifier: %s', pv)
                continue
            project_version, proj, ver, modname = parse_projectversion(pv, logfn=logfn)
            filename, code, loader = pth_import(
                    modname, fallback_paths, projectversion=project_version,
                    loginfo=logfn
                    )
            # First wins
            pvmod[pv] = modname
            modcode[modname] = (filename, code, loader)

        logfn(' '.join(sys.argv))
        if o.get('modulename'):
            modname = o['modulename']
            sys.argv[:] = [modname] + args
            if modname in modcode:
                filename, code, loader = modcode[modname]
            else:
                filename, code, loader = pth_import(
                        o['modulename'], fallback_paths
                        )
                modcode[modname] = (filename, code, loader)
            return _run_module_code(code, ns, o['run_name'],
                            filename, loader, True)
        elif o.get('command'):
            sys.argv[:]=args
            sys.argv[:]=['-c'] + args
            logfn(' '.join(sys.argv))
            exec o['command'] in ns

    except SystemExit:
        raise
    except Exception:
        if o['debug']:
            exc_info = sys.exc_info()
            import pdb, traceback
            traceback.print_exception(*exc_info)
            sys.stderr.write('\nStarting pdb:\n')
            pdb.post_mortem(exc_info[2])
        else:
            raise

if __name__=='__main__':
    main2()

