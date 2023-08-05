"""
$Id: setup.py 86 2007-05-25 20:51:57Z fairwinds $

zif.jsonserver
Copyright (c) 2006, Virginia Polytechnic Institute and State University
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Distutils setup
 
"""


import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'zif.jsonserver',
    version = '0.6',
    license = 'ZPL2.1 and LGPL',
    description = 'A json server for zope 3.',
    long_description = (
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zif', 'jsonserver', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    keywords = 'jsonserver json zope3',
    author = 'Jim Washington and contributors',
    author_email = 'jwashin@users.sourceforge.net',
    url = 'http://zif.svn.sourceforge.net/viewvc/zif/zif.jsonserver',
    classifiers = [
       'Framework :: Buildout',
       'Framework :: Zope3',
       'Intended Audience :: Developers',
       'Development Status :: 5 - Production/Stable',
       'Environment :: Web Environment',
       'License :: OSI Approved :: Zope Public License',
       'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
       'Operating System :: OS Independent',
       'Programming Language :: Python',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['zif'],
    install_requires = ['setuptools'],
    dependency_links = ['http://download.zope.org/distribution/'],   
    include_package_data = True,
    zip_safe = False,
    )
