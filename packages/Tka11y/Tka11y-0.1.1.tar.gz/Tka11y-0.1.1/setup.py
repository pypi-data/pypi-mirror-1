#!/usr/bin/env python

# Setup for Tka11y - Accessibility-aware Tkinter.

from distutils.core import setup

TKA11Y_VERSION = (0, 1, 1)

# Convert version tuple to a string for consumption elsewhere.
versionString = '.'.join(str(part) for part in TKA11Y_VERSION)

# Write version to an internal module for consumption by the constants module.
versionFile = open('Tka11y/version.py', 'w')
versionFile.write('Version = %s\n' % (TKA11Y_VERSION,))
versionFile.write('VersionString = %s\n' % (repr(versionString),))
versionFile.close()

setup(
    name='Tka11y',
    version=versionString,
    description='Accessibility-aware Tkinter',
    long_description=open('README.txt', 'r').read(),
    author='Allen B. Taylor',
    author_email='a.b.taylor@gmail.com',
    url='http://pypi.python.org/pypi/Tka11y',
    packages=[
        'Tka11y',
        ],
    requires=[
        'papi(>=0.0.9)',
        ],
    )
