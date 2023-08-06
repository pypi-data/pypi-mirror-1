"""
$Id: setup.py 1917 2008-08-29 22:11:37Z lucielejard $

Copyright (c) 2007 - 2008 ifPeople, Kapil Thangavelu, and Contributors
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Distutils setup
 
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='getpaid.nullpayment',
    version='0.3',
    license = 'BSD',
    author='Getpaid Community',
    author_email='getpaid-dev@googlegroups.com',
    description='Get paid null payment process functionality',
    long_description = (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'getpaid', 'nullpayment', 'README.txt')
        + '\n'
        ),
    classifiers = [
        "Framework :: Plone",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
        ],
    url='http://code.google.com/p/getpaid',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['getpaid'],
    include_package_data=True,
    install_requires = ['setuptools',
                        'getpaid.core',
                        'zope.app.annotation',
                       ],
    zip_safe = False,
    )
