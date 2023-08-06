# koboldfs
# Copyright (C) 2008-2009 Fabio Tranchitella <fabio@tranchitella.it>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
from setuptools import setup, find_packages

long_description = open('README.txt', 'r').read()
long_description += '\n'
long_description += open('CHANGES.txt', 'r').read()

setup(
    name="koboldfs",
    description='application-level distributed file system written in Python',
    long_description=long_description,
    author="Fabio Tranchitella",
    author_email="kobold@debian.org",
    url='http://pypi.python.org/pypi/koboldfs',
    version='0.2.2',
    license = 'GPL-2',
    packages=['koboldfs', 'koboldfs.zope'],
    package_dir = {'': 'src'},
    entry_points = {
        'console_scripts': ['koboldfsd = koboldfs.server:main',]
    },
    tests_require=[
        'zope.testing',
    ],
    install_requires=[
        'setuptools',
    ],
    extras_require=dict(
        zope=[
            'zope.component [zcml]',
            'zope.configuration',
            'zope.interface',
            'zope.schema',
            'zope.thread',
        ]
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Filesystems',
        'License :: DFSG approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Framework :: Setuptools Plugin',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    zip_safe=False,
)
