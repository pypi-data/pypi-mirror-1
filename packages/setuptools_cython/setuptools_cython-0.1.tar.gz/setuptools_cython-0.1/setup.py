#!/usr/bin/env python
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
from setuptools import setup

__doc__ = """
Allows compiling Cython extensions in setuptools
by putting setuptools_cython in your setup_requires.

Usage
=====

Use setuptools, add setuptools_cython to your setup_requires.

Some verbatim code is required to make Extension behave as expected.

Usage example
=============

setup.py::

    #!/usr/bin/env python

    from setuptools import setup
    from distutils.extension import Extension

    # setuptools DWIM monkey-patch madness
    # http://mail.python.org/pipermail/distutils-sig/2007-September/thread.html#8204
    import sys
    if 'setuptools.extension' in sys.modules:
        m = sys.modules['setuptools.extension']
        m.Extension.__dict__ = m._Extension.__dict__

    setup(
            name = "example",
            version = "0.1",
            description="setuptools_cython example",
            setup_requires=[
                'setuptools_cython',
                ],
            ext_modules=[
                Extension('example', ['example.pyx']),
                ],
            )

"""

setup(
        name='setuptools_cython',
        version='0.1',
        author='Gabriel de Perthuis',
        author_email='gabriel.de-perthuis@c-s.fr',
        url='http://pypi.python.org/pypi/setuptools_cython/',
        description='Cython setuptools integration',
        long_description=__doc__,
        license='http://www.gnu.org/licenses/gpl-2.0.html',
        py_modules=['setuptools_cython', ],
        install_requires=[
            'Cython',
            ],
        entry_points={
            # Can't override build_ext with an entry point.
            # This means we can't collide on ext_modules either.
            # So we create a cython_ext_modules to hold pyx files.

            # There's still a problem: our extra command isn't invoked automatically.
            # Even though it appears to be a subcommand of build.

            # The only way out would be an alias, and that means getting rid
            # of our parameter. And it doesn't work either, aliases are only expanded
            # when they are on the command line.

            # This means distutils integration using distutils extension points
            # is an impossibility.
            # But we have our own entry point!
            # Take advantage of the parameter validation.
            # In fact, we can write a 'validation' for the original ext_modules
            # parameter.

            'distutils.commands': [
                #'build_cython = setuptools_cython:build_cython',
                ],
            'distutils.setup_keywords': [
                'ext_modules = setuptools_cython:ext_modules_hack',
                #'cython_ext_modules = setuptools_cython:validate_cython_ext_modules',
                ],

            },
        classifiers=[
            'Framework :: Setuptools Plugin',
            'Topic :: Software Development :: Build Tools',
            ],
        )

