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
"""Setup for zope.app.appsetup package

$Id: setup.py 98258 2009-03-19 09:19:20Z nadako $
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.app.appsetup',
    version='3.10.0',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description="Zope app setup helper",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords="zope3 app setup",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/zope.app.appsetup',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    extras_require=dict(test=['zope.app.testing']),
    namespace_packages=['zope', 'zope.app'],
    install_requires=['setuptools',
                      'zope.app.component',
                      'zope.app.publication',
                      'zope.component',
                      'zope.configuration',
                      'zope.container',
                      'zope.error',
                      'zope.event',
                      'zope.interface',
                      'zope.location',
                      'zope.session',
                      'zope.site',
                      'zope.security',
                      'zope.traversing',
                      'ZODB3',
                      ],
    include_package_data=True,
    zip_safe=False,
    entry_points = """
        [console_scripts]
        debug = zope.app.appsetup.debug:main
        """,
    )
