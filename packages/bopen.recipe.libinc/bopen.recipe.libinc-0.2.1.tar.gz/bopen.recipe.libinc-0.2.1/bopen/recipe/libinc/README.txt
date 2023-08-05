
Warning: Work in progress
=========================

This zc.buildout recipe is pre-alpha quality.

Supported options
=================

flags-command
    a list of commands that return the linking options, one per line

Example usage
=============

We'll use a simple config command to demonstrate the recipe.

    >>> import os.path
    >>> testdata = join(os.path.dirname(__file__), 'testdata')
    >>> ls(testdata)
    d .svn
    - sample-config

The options are accessible by other recipes:

    >>> mkdir(sample_buildout, 'recipes')
    >>> write(sample_buildout, 'recipes', 'echo.py',
    ... """
    ... import logging
    ...
    ... class Echo:
    ...     def __init__(self, buildout, name, options):
    ...         self.name, self.options = name, options
    ...
    ...     def install(self):
    ...         logging.getLogger(self.name).info(self.options.get('echo', ''))
    ...         return ()
    ...
    ...     def update(self):
    ...         pass
    ... """)

    >>> write(sample_buildout, 'recipes', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "recipes",
    ...     entry_points = {'zc.buildout': ['echo= echo:Echo']},
    ...     )
    ... """)

Let's create a buildout to build and install the package.

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop = recipes
    ... parts = package
    ...
    ... [package]
    ... recipe = recipes:echo
    ... echo =
    ...     include-dirs: ${config-package:include-dirs}
    ...     library-dirs: ${config-package:library-dirs}
    ...     libraries: ${config-package:libraries}
    ...     cflags: ${config-package:cflags}
    ...     ldflags: ${config-package:ldflags}
    ...
    ... [config-package]
    ... recipe = bopen.recipe.libinc
    ... flags-command =
    ...     %(testdata)s/sample-config --cflags
    ...     %(testdata)s/sample-config --libs
    ...     %(testdata)s/sample-config --version
    ... include-dirs = /usr/include/mysample
    ... library-dirs = /usr/lib/mysample
    ... libraries = mysample
    ... """ % {'testdata': testdata})


    >>> print system(buildout + ' -N')
    Develop: ...
    config-package: .../testdata/sample-config --cflags -> -I/usr/include -I/usr/include/sample
    config-package: .../testdata/sample-config --libs -> -L/usr/lib -L/usr/lib/sample -lsample -lsample_rt
    config-package: .../testdata/sample-config --version -> 1.0
    config-package: 
        include-dirs: /usr/include /usr/include/sample /usr/include/mysample
        library-dirs: /usr/lib /usr/lib/sample /usr/lib/mysample
        libraries: sample sample_rt mysample
        cflags: -I/usr/include -I/usr/include/sample -I/usr/include/mysample
        ldflags: -L/usr/lib -L/usr/lib/sample -L/usr/lib/mysample -lsample -lsample_rt -lmysample
    Installing config-package.
    Installing package.
    package:
        include-dirs: /usr/include /usr/include/sample /usr/include/mysample
        library-dirs: /usr/lib /usr/lib/sample /usr/lib/mysample
        libraries: sample sample_rt mysample
        cflags: -I/usr/include -I/usr/include/sample -I/usr/include/mysample
        ldflags: -L/usr/lib -L/usr/lib/sample -L/usr/lib/mysample -lsample -lsample_rt -lmysample
