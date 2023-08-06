##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for repoze.recipe.egg package

$Id: setup.py 81447 2007-11-03 19:14:30Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def alltests():
    # use the zope.testing testrunner machinery to find all the
    # test suites we've put under ourselves
    from zope.testing.testrunner import get_options
    from zope.testing.testrunner import find_suites
    from zope.testing.testrunner import configure_logging
    configure_logging()
    from unittest import TestSuite
    import sys
    here = os.path.abspath(os.path.dirname(sys.argv[0]))
    args = sys.argv[:]
    defaults = ['--test-path', here]
    options = get_options(args, defaults)
    suites = list(find_suites(options))
    return TestSuite(suites)

name = "repoze.recipe.egg"
setup(
    name = name,
    version = "0.3",
    author = "Jim Fulton (forked by Chris McDonough)",
    author_email = "chrism@plope.com",
    description = "Recipe for installing Python package distributions as eggs",
    long_description = (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('repoze', 'recipe', 'egg', 'README.txt')
        + '\n' +
        read('repoze', 'recipe', 'egg', 'selecting-python.txt')
        + '\n' +
        read('repoze', 'recipe', 'egg', 'custom.txt')
        + '\n' +
        read('repoze', 'recipe', 'egg', 'api.txt')
        + '\n' +
        'Download\n'
        '*********\n'
        ),
    keywords = "development build",
    classifiers = [
       'Development Status :: 5 - Production/Stable',
       'Framework :: Buildout',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    url='http://svn.repoze.org/repoze.recipe.egg/trunk/',
    license = "ZPL 2.1",

    packages = find_packages(),
    namespace_packages = ['repoze', 'repoze.recipe'],
    install_requires = [
        'zc.buildout >=1.0.0b3',
        'setuptools',
        ],
    tests_require = ['zope.testing', 'zc.buildout >=1.0.0b3'],
    #test_suite = name+'.tests.test_suite',
    test_suite = '__main__.alltests',
    entry_points = {'zc.buildout': ['default = %s:Scripts' % name,
                                    'script = %s:Scripts' % name,
                                    'scripts = %s:Scripts' % name,
                                    'eggs = %s:Eggs' % name,
                                    'custom = %s:Custom' % name,
                                    'develop = %s:Develop' % name,
                                    ]
                    },
    include_package_data = True,
    zip_safe=False,
    )
