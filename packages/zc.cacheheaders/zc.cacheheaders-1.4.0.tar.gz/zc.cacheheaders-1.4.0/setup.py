##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
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
import os
import setuptools
from setuptools import setup, find_packages

setuptools.setup(
    name="zc.cacheheaders",
    version="1.4.0",
    description="Cache control utility functions",
    keywords="development build macro",
    classifiers = [
       'Framework :: Zope3',
       'Intended Audience :: Developers',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    author="Aaron Lehmann",
    author_email="aaron@zope.com",
    license="ZPL 2.1",

    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    namespace_packages=["zc",],
    install_requires=[
        "setuptools",
        "zc.recipe.testrunner",
        "zope.testing",
        "zope.publisher",
        ],
    include_package_data=True,
    zip_safe=False,
    )
