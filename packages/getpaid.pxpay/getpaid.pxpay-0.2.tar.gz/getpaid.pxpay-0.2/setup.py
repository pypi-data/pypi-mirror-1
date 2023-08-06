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
    name="getpaid.pxpay",
    version="0.2",
    author='getpaid community',
    author_email='getpaid-dev@googlegroups.com',
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
    long_description = (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'getpaid', 'pxpay', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    packages=find_packages('src'),
    package_dir={'':'src'},
    description = "PXPay payment plugin",
    license = "ZPL",
    keywords = "getpaid pxpay payment",
    namespace_packages=['getpaid'],
    include_package_data=True,
    install_requires = [ 'setuptools',
                         'getpaid.core',
                         'getpaid.wizard',
                         'zope.interface',
                         'zope.component',
                         'zope.formlib',
                         'zc.ssl',
                         'zc.table',
                         'elementtree',
                         'Products.PloneGetPaid',
                         'hurry.workflow',
                         'zope.schema',
                         ],
    zip_safe = False,
    )
