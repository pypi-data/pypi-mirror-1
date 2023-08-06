"""
$Id: setup.py 1868 2008-08-22 22:00:38Z fairwinds.dp $

Copyright (c) 2007 - 2008 ifPeople, Kapil Thangavelu, and Contributors
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Distutils setup
 
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='getpaid.paymentech',
    version='0.3',
    license = 'ZPL2.1',
    author='Six Feet Up, Inc.',
    author_email='getpaid-dev@googlegroups.com',
    description='Get paid paymentech payment processor functionality',
    long_description = (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'getpaid', 'paymentech', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Framework :: Zope3",
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
                        'zc.ssl',
                        'zope.app.annotation',
                       ],
    zip_safe = False,
    )

