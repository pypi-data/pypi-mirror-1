"""
$Id: setup.py 67 2007-04-14 02:01:59Z fairwinds $

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
    version = '0.1',
    license = 'ZPL2.1',
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
    author = 'Jim Washington',
    author_email = 'jwashin@users.sourceforge.net',
    url = 'http://zif.svn.sourceforge.net/viewvc/zif/zif.jsonserver',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['zif'],
    install_requires = ['setuptools'],
    dependency_links = ['http://download.zope.org/distribution/'],   
    include_package_data = True,
    zip_safe = False,
    )
