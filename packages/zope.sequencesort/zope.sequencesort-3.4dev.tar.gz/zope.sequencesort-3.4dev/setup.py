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
"""zope.sequencesort setup

$Id: setup.py 73091 2007-03-09 03:37:18Z baijum $
"""

from setuptools import setup, find_packages

setup(
    name="zope.sequencesort",
    version="3.4dev",
    url='http://svn.zope.org/zope.sequencesort',
    license='ZPL 2.1',
    description='Zope sequencesort',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zope'],
    include_package_data=True,
    install_requires = ['setuptools'],
    zip_safe = False
    )
