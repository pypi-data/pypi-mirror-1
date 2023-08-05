"""
$Id: setup.py 64 2007-04-14 01:38:22Z fairwinds $

zif.jsmin
Copyright (c) 2006, Virginia Polytechnic Institute and State University
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Distutils setup
 
"""


import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'zif.jsmin',
    version = '0.2',
    license = 'BSD',
    description = 'WSGI middleware for javascript compression.',
    long_description = (
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zif', 'jsmin', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    keywords = 'jsmin wsgi middleware zope3',
    author = 'Jim Washington',
    author_email = 'jwashin@users.sourceforge.net',
    url = 'http://zif.svn.sourceforge.net/viewvc/zif/zif.jsmin',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['zif'],
    install_requires = ['setuptools'],    
    include_package_data = True,
    zip_safe = False,
    )
