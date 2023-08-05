"""
$Id: setup.py 47 2007-04-12 03:43:37Z fairwinds $

zif.gzipper
Copyright (c) 2006, Virginia Polytechnic Institute and State University
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Distutils setup
 
"""
import os
from setuptools import setup, find_packages

name = 'zif.gzipper'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = name,
    version = '0.1',
    license = 'BSD',
    description = 'WSGI middleware providing gzip compression for HTTP server output.',
    long_description =(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zif', 'gzipper', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    keywords ='gzipper gzip wsgi middleware zope3',
    author = 'Jim Washington',
    author_email = 'jwashin@users.sourceforge.net',
    url = 'http://zif.svn.sourceforge.net/viewvc/zif/zif.gzipper',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['zif'],
    install_requires = ['setuptools'],    
    include_package_data = True,
    zip_safe = False,
    )
