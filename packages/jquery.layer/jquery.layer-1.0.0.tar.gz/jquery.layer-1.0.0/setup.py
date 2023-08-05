##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup

$Id: setup.py 81256 2007-10-31 01:15:51Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='jquery.layer',
      version='1.0.0',
      author = "Roger Ineichen and the Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "Base layers for JQuery functionality",
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      license = "ZPL 2.1",
      keywords = "zope3 layer jquery viewlet",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/jquery.layer',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['jquery'],
    extras_require = dict(
        test = ['zope.testing'],
        ),
    install_requires = [
        'setuptools',
        'zope.publisher',
        'zope.viewlet',
        ],
    include_package_data = True,
    zip_safe = False,
    )
