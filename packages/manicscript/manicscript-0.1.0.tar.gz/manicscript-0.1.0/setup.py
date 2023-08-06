#!/usr/bin/env python

kw = dict(
    name='manicscript',
    version='0.1.0',
    description='Python and JavaScript libraries for event-driven interactive web applications',
    url='http://pypi.python.org/pypi/manicscript/',
    author='Jason Alonso',
    author_email='jalonso@media.mit.edu',
    packages=['manicscript'])

try:
    from setuptools.core import setup
    kw['install_requires'] = ['stomper']
except ImportError:
    from distutils.core import setup

setup(**kw)

