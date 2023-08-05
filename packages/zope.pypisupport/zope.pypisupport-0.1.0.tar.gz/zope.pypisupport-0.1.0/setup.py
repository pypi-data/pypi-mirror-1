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
"""Setup for ``zope.pypisupport`` project

$Id: setup.py 81552 2007-11-05 21:37:07Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.pypisupport',
    version='0.1.0',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    description='Zope Viewlets',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords = "pypi console tools",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'],
    url='http://cheeseshop.python.org/pypi/zope.pypisupport',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['zope'],
    install_requires=[
        'lxml',
        'setuptools',
        'zope.testbrowser',
        ],
    entry_points = dict(console_scripts=[
        'addrole = zope.pypisupport.role:addrole',
        'delrole = zope.pypisupport.role:delrole',
        ]),
    include_package_data = True,
    zip_safe = False,
    )
