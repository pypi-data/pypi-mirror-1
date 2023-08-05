##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.app.error package

$Id: setup.py 80200 2007-09-27 08:40:41Z batlogg $
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.error',
    version = '3.5.1',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    description = "Error reporting utility management UI for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords = "zope3 error reporting utility views UI",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://cheeseshop.python.org/pypi/zope.app.error',
	packages=find_packages('src'),
	package_dir = {'': 'src'},
    extras_require=dict(
        test=['zope.app.testing']),
    namespace_packages=['zope', 'zope.app'],
    install_requires=['setuptools',
                      'zope.exceptions',
                      'zope.error',
                      'zope.app.appsetup',
                      'zope.publisher',
                      'zope.app.container',
                      ],
    include_package_data = True,

    zip_safe = False,
    )
