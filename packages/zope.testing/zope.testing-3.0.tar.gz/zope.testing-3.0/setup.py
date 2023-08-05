##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for zope.testing package

$Id$
"""

import os

try:
    from setuptools import setup
except ImportError, e:
    from distutils.core import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

chapters = '\n'.join([
    read('src', 'zope', 'testing', name)
    for name in (
    'testrunner.txt',
    'testrunner-simple.txt',
    'testrunner-layers-api.txt',
    'testrunner-layers.txt',
    'testrunner-arguments.txt',
    'testrunner-verbose.txt',
    'testrunner-test-selection.txt',
    'testrunner-progress.txt',
    'testrunner-errors.txt',
    'testrunner-debugging.txt',
    'testrunner-layers-ntd.txt',
    'testrunner-coverage.txt',
    'testrunner-profiling.txt',
    'testrunner-wo-source.txt',
    'testrunner-repeat.txt',
    'testrunner-gc.txt',
    'testrunner-leaks.txt',
    'testrunner-knit.txt',
    'formparser.txt',
    )])
    
setup(
    name='zope.testing',
    version='3.0',
    url='http://svn.zope.org/zope.testing',
    license='ZPL 2.1',
    description='Zope testing framework, including the testrunner script.',
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' + chapters + '\n'
        'Download\n'
        '**********************\n'
        ),
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    
    packages=["zope", "zope.testing"],
    package_dir = {'': 'src'},
    
    namespace_packages=['zope',],
    extras_require={'zope_tracebacks': 'zope.exceptions'},
    include_package_data = True,    
    zip_safe = False,
    )
