#! /usr/bin/env python
# (C) Copyright 2007 Nuxeo SAS <http://nuxeo.com>
# Author: bdelbosc@nuxeo.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#
"""PLUSH = Python LUcene SHell

$Id: setup.py 51226 2007-02-22 09:42:15Z bdelbosc $
"""
from distutils.core import setup

from plush.version import __version__
from tests.distutilstestcommand import TestCommand

setup(
    name="plush",
    version=__version__,
    description="Python LUcene SHell.",
    long_description="""\
A simple Lucene interactive terminal.

Main features:

* View store information.

* View indexes definition.

* Search using the Lucene Query Parser Syntax.

* Sort result list.

* Browse by document number.

* Top term occurences for a field, matching a regex.

* Support PyLucene 1.9.1 and 2.0.0.

* Interactive shell emacs like command history and editing features.

* Command line tool and thus scriptable.

* Easy installation, no java required.

* Plush is free software distributed under the GNU GPL.

* Plush is written in python and can be easily customized.

""",
    author="Benoit Delbosc",
    author_email="bdelbosc@nuxeo.com",
    url="http://public.dev.nuxeo.com/~ben/plush/",
    download_url="http://public.dev.nuxeo.com/~ben/plush/plush-%s.tar.gz"%__version__,
    license='GPL',
    packages=['plush'],
    package_dir={'plush': 'plush'},
    scripts=['scripts/plush',
             ],
    keywords='Lucene Pylucene command line shell terminal tool',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    cmdclass = { 'test': TestCommand,}
)
