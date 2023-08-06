#! /usr/bin/env python
# (C) Copyright 2009 Supreet Sethi <http://chasingframes.co.cc>
# Author: supreet.sethi@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
#
"""svnbackup package setup

"""
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
#from distutils.core import setup
from svnpuppy import __version__
setup(
    name="svnpuppy",
    version=__version__,
    description="Subversion backup script",
    long_description="""\
Subversion repository backup
* Can backup a single repository or set of repositories existing under 
  a top level directory

* Capable of doing a incremental backup

* Handles compression 

* Requires only svnadmin installed in path

""",
    author="Supreet Sethi",
    author_email="supreet.sethi@gmail.com",
    url="http://chasingframes.co.cc",
    license='GPL',
    keywords='administration backup scm svn versioncontrol',
    packages= ['.'],
    entry_points = {
        'setuptools.installation': [
            'svnpuppy = svnpuppy.svnpuppy.__main__'
            ]
        },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Archiving :: Backup',
    ],
    # setuptools specific keywords
    install_requires = [],
    zip_safe=True,
    package_data={},
    )
