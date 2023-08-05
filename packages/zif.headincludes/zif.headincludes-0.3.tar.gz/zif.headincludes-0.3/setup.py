"""
$Id: setup.py 88 2007-05-25 23:28:02Z fairwinds $

zif.headincludes
Copyright (c) 2006, Virginia Polytechnic Institute and State University
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Distutils setup
 
"""


import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'zif.headincludes',
    version = '0.3',
    license = 'BSD',
    description = 'WSGI middleware to manipulate css and javascript in the HTML header.',
    long_description = (
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zif', 'headincludes', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    keywords = 'headincludes wsgi middleware zope3',
    author = 'Jim Washington and contributors',
    author_email = 'jwashin@users.sourceforge.net',
    url = 'http://zif.svn.sourceforge.net/viewvc/zif/zif.headincludes',
    classifiers = [
       'Framework :: Buildout',
       'Framework :: Zope3',
       'Intended Audience :: Developers',
       'Development Status :: 5 - Production/Stable',
       'Environment :: Web Environment',
       'License :: OSI Approved :: BSD License',
       'Operating System :: OS Independent',
       'Programming Language :: Python',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['zif'],
    install_requires = ['setuptools'],    
    include_package_data = True,
    zip_safe = False,
    )
