Usage: pyrun.py  [-nidDpP] [BASEPATH(s)][-m mod.name | '--'] [TARGET-OPTIONS]

In most cases the solo '--' is not required. It tends to be useful when you
implicitly select the module to run AND you want to pass a non option argument
as the first value in the command line for that module. It can also be
necessary when the target module has short options, without long-name
alternatives, which collide with those defined for pyrun.

Discover python packages and modules under PATH. Run the first module file
named in `PATH` *OR* explicitly nominated using the `-m` option.

NOTE: Any option that is marked [NYI] is Not Yet Implemented.

Options:
  -h, --help         show this help message and exit
  --log-level=LEVEL  [default:WARNING] set the logging level, any string which
                     names a log level which is defined by the logging package
                     is allowed. For example any of CRITICAL, WARNING, INFO
                     and DEBUG (in increasing order of verbosity)
  -q                 Suppress all warnings about missing paths etc. Useful
                     when you are using speculative paths and are using -p or
                     -P to print the discoverd path.
  -p                 Print the discovered path
  -P                 Print the discovered path in a PYTHONPATH compatible
                     format
  -n                 NORUN. Don't run any of the modules implied by module
                     file references in  the discovery path.
  -C SCRIPT          Identify a *python* SCRIPT to execute. The script need
                     not have file extension but it must contain leagal python
                     code. This option trumps -m. This option should only be
                     necessary when the launcher for the python program you
                     wish to run contains significant functionality. No
                     additions are made to the discovery path or sys.path as a
                     result of using this option. If the target script imports
                     a related package you will need to include additional non
                     option arguments to discover its path.
  -m MODULE          Explicitly select a module to run. (trumped by -S)
  -d                 DEBUG session. Use `pdb.runeval` on the module code in
                     order to enter an interactive debug session at the first
                     python statement of the target module
  -D                 POSTMORTEM debugging. If the target raises an exception,
                     start a     postmortem pdb debugging session.
  -i                 INTERACTIVE session with prepared sys.argv and sys.path.
  -c STATEMENT       Update sys.argv and sys.path then execute the statement
                     in a new, clean, module context.
  -x EXCLUDE         Exclude one or more directories, separated by ":", from
                     the discovery path.
  -X PRUNE           Prune all paths which contain this value from the set of
                     paths which *were* discovered. Specify multiple -X
                     options if you wish too prune based on more than one
                     string.
