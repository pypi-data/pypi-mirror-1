mkcode
======

mkcode is a system for performing make-style development tasks.  It provides execution of dependencies, a console script for calling tasks, and automatic discovery of the distutils commands found in setup.py.  It does not provide tools for compiled languages or complex nested builds (look to SCons or zc.buildout for those).

Tasks are defined as plain python functions, decorated with a special ``@task`` decorator.  The name of the function becomes the name of the task, and that task may be called from the command-line via the ``mk`` script.

A file in the project's root directory named ``mkfile.py`` contains all of the task definitions.  The ``mk`` script, when invoked, imports the tasks.

Here is an example ``mkfile.py``::

  from mkcode import *

  @task
  def clean():
      """ Clean out all .pyc files in sub-directories """
      # This is *great* for getting rid of those stale .pyc files
      # that cause mysterious test failures.
      for pyc in path().relpath().walkfiles('*pyc'):
          print 'Removing:', pyc
          pyc.remove()
  
  setup = namespace('setup')  # the distutils commands from 'setup.py'

  # re-define the 'test' target
  task('test', [clean, setup.test])

Here is how you run our new ``test`` target::

  $ mk test

We can still run the original setuptools ``test`` target using the ``setup`` namepace::

  $ mk setup.test

Please see ``mkfile.py`` in the distribution's base directory for more task examples.

Tasks may belong to namespaces.  Namespace tasks are called by joining the namespace and task name with a dot, as if you were referencing a Python object attribute::

  # call the 'bar' task in the 'foo' namespace
  $ mk foo.bar

Please see `Jeff Shell's post <http://griddlenoise.blogspot.com/2007/04/pythons-make-rake-and-bake-another-and.html>`_ for examples of how a namespace may be defined.

The ``setup`` namespace is defined by default, and contains all of the commands exported by setuptools.  However, setuptools' commands are a special case, and they are also made available in the root namespace.  Invoking them does not require that you prefix them with ``setup.`` Therefore the following three commands are equivalent::

  $ mk develop
  $ mk setup.develop
  $ python setup.py develop

Extra command-line parameters are passed through to their targets. The following two commands are equivalent::

  $ mk rotate --help
  $ python setup.py rotate --help

The ``mk`` script takes a number of command-line switches, notably ``-T``, which lists all of the registered tasks, ``-n``, which runs a task and its dependencies without executing them, and ``-f``, which allows you to specify an alternative mkfile.


Known Issues
------------

The program fails on vanilla ``setup.py`` files that define their own commands.  The Python Imaging Library, PIL, is one example of this.

Acknowledgments
---------------

This program was heavily inspired by `Jeff Shell's in-house build system <http://griddlenoise.blogspot.com/2007/04/pythons-make-rake-and-bake-another-and.html>`_.  The example targets Jeff provided should work in this system with little modification.

Path support is greatly enhanced by Jason Orendorff's excellent `path <http://www.jorendorff.com/articles/python/path/>`_ module.  I highly recommend it for **all** of your Python work.
