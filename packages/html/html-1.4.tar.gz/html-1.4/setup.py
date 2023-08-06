#! /usr/bin/env python

from distutils.core import setup

from html import __version__, __doc__

# perform the setup action
setup(
    name = "html",
    version = __version__,
    description = "simple, elegant HTML generation",
    long_description = __doc__,
    author = "Richard Jones",
    author_email = "rjones@ekit-inc.com",
    py_modules = ['html'],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: BSD License',
    ],
)

# vim: set filetype=python ts=4 sw=4 et si
