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

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__),
                             'ro', 'bdb', 'cmmi', *rnames)).read()

version = "1.0.2"

name = "ro.bdb.cmmi"
setup(
    name = name,
    version = version,
    author = "Reed O'Brien",
    author_email = "reed@koansys.com",
    description = "ZC Buildout recipe for BDB configure/make/make install",
    license = "ZPL 2.1",
    keywords = "zope3",
    url='http://www.python.org/pypi/'+name,
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('README.txt')
        + '\n' +
        'Download Cache\n'
        '**************\n'
        'The recipe supports use of a download cache in the same way\n'
        'as zc.buildout. See downloadcache.txt for details\n'
        + '\n' +
        'Download\n'
        '**********************\n'
        ),

    packages = find_packages(),
    include_package_data = True,
    data_files = [('.', ['README.txt'])],
    namespace_packages = ['ro', 'ro.bdb'],
    install_requires = ['zc.buildout', 'setuptools'],
    entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
    zip_safe = True,
    )
