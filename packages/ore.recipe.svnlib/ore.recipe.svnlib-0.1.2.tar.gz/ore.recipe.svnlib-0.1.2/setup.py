##############################################################################
#
# Copyright (c) 2008 Kapil Thangavelu <kapil.foss@gmail.com>
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
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = "ore.recipe.svnlib"

setup(
    name = name,
    version = "0.1.2",
    author = "Kapil Thangavelu",
    author_email = "kapil.foss@gmail.com",
    description = "Buildout recipe for compiling python subversion bindings",
    long_description=read('ore','recipe','svnlib', 'README.txt'),
    license = "ZPL 2.1",
    keywords = "zope3 subversion svn",
    url='http://www.python.org/pypi/'+name,
    packages = find_packages(),
    namespace_packages = ['ore', 'ore.recipe'],
    package_data = { '': ['*.txt'] },
    install_requires = ['zc.buildout', 'zc.recipe.cmmi', 'setuptools'],
      classifiers=['Programming Language :: Python',
                   'Framework :: Buildout',
                   'Intended Audience :: Developers',
                   'Operating System :: Unix',
                   'Topic :: Software Development :: Version Control',
                   'Topic :: System :: Software Distribution',
                   'License :: OSI Approved :: Zope Public License',
                   ],    
    entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
    zip_safe = True,
    )
