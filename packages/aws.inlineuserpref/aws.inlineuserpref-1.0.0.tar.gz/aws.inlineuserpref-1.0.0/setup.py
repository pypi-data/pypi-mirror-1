# -*- coding: utf-8 -*-
# Copyright (c) 2009 'Alter Way Solutions'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""aws.inlineuserpref setup"""

from setuptools import setup, find_packages
import os

def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = _textFromPath('aws', 'inlineuserpref', 'version.txt')

long_description = '\n\n'.join([
    _textFromPath('README.txt'),
    _textFromPath('docs', 'HISTORY.txt')])

setup(
    name='aws.inlineuserpref',
    version=version,
    description="Per user Plone inline KSS editing preference",
    long_description=long_description,
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable"
        ],
    keywords='plone kss preferences',
    author='Gilles Lenfant',
    author_email='gilles.lenfant@ingeniweb.com',
    url='http://plone.org/products/aws-inlineuserpref',
    license='GPL',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['aws'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
