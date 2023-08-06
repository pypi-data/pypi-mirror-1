#!/usr/bin/env python

packages = [
    'manicscript',
    'manicscript.twisted',
    'manicscript.djchat',
    'manicscript.replay',
    'manicscript.kerby',
    'manicscript.crypto',
    'manicscript.jsoncore']


kw = dict(
    name='manicscript',
    version='0.1.1',
    description='Python and JavaScript libraries for event-driven interactive web applications',
    url='http://pypi.python.org/pypi/manicscript/',
    author='Jason Alonso',
    author_email='jalonso@media.mit.edu',
    packages=packages)

try:
    from setuptools import setup, find_packages
    kw['install_requires'] = ['stomper']

    # Verify the list of packages.
    setuptools_packages = find_packages(exclude=['comsat', 'comsat.*'])
    if set(packages) != set(setuptools_packages):
        import sys
        print >>sys.stderr, 'Missing or extraneous packages found.'
        sys.exit(1)

except ImportError:
    from distutils.core import setup

setup(**kw)

