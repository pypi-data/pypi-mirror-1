pyrun
~~~~~

.. _distutils python terms: http://docs.python.org/dist/python-terms.html
.. _distutils distutils terms: http://docs.python.org/dist/distutils-terms.html
.. _setuptools terms: http://mail.python.org/pipermail/distutils-sig/2005-June/004652.html

You can access the most commonly useful features of `pyrun`, without installing
the project, by running the ``pyrun.py`` file directly.

For example, the following::

  cd ~
  wget http://svn.wiretooth.com/svn/open/pyrun-trunk/pyrun.py
  ``python ~/pyrun.py  ~/my/python/libs ~/my/python/scripts/go.py``

Is all you need in order to run the `go.py` module with a sys.path
automatically discovered from directories under `~/my/python/libs`. You can
list an arbitrary number of directories and paths to actual python files. The
order you list them controls the order in which the path extension entries are
built. The resulting path will not contain any duplicates. Each entry in the
path extension will be a legitimate import path.

Note:
  A setup.py file is provided - with suitable egg entry point declarations 
  - if you prefer this.


For each argument which identifies a python file  `pyrun` will locate the root
package directory and add that to the path. The *absolute* dotted module name
of the first python file you identify in this way is the module that will, by
default, be executed as __main__. You can explicitly override this choice by
using pyrun's ``-m`` option.

Note:
    root package is the parent directory of the "top most package" see
    `distutils python terms`_ and `distutils distutils terms`_


The delimiter between the `pyrun` arguments and options and the options for the
target module is the first non option argument encountered after the discovery
paths. If that option is a `pyrun` option (see ``pyrun --help`` for the list)
then `pyrun` takes it and passes all remaining arguments to the target module
in a suitably massaged ``sys.argv``.

If the target module takes arguments but does not naturally accept an option
as its first argument (python setup.py install is the classic example) then
you can artificially terminate the `pyrun` options with ``--``.

For example it is possible to run the setup script of the `pyrun` project in
the following ways

  * If you have setup tools installed::

      python setup.py bdist_egg

  * If your python distribution has *not* removed distutls from the python
    standard library::

      python setup.py sdist

  * If you have a copy of the setuptools egg in ``../python/eggs``::

      python pyrun.py ../python/eggs -m setup bdist_egg
      python pyrun.py ../python/eggs setup.py -- bdist_egg


If you have a directory which contains a docutils source tree or installation
then adding that to the discovery path will let the setup.py script build
*this* documentation.

If none of the non option arguments identify a python module file *and* you
dont explicitly select one using ``-m`` then `pyrun` will simply print the path
it has discovered and exit. You can force `just print the path` using ``-p``
or ``-P``

`pyrun` is reasonably smart in respect of python egg distributions. When
multiple egg distributions of the same project are found on the discovery path
only the *best* version found is included in the path extension. Eggs which are
not compatible with the current python interpreter are ignored. The measure of
`best egg for a project` uses the same algorithm as used by the
pkg_resources.py module distributed by the setuptools project.

Note:
  The current version does not filter out incompatible `platforms` for eggs
  that contain c extensions - see `pyrun.filter_best_eggs` if you have time on
  your hands, its not to much work to add this check.

The issue tracker for this package can be found at:

http://trac.wiretooth.com/public/wiki/pyrun

When opening a ticket please assign it to the `pyrun` component or, at least,
mention `pyrun` in your ticket summary.

