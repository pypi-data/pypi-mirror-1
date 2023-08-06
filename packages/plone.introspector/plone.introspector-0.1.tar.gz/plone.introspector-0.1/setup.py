##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Setup for zope.introspector package

$Id: setup.py 74408 2008-10-24 16:05:30Z mlundwall $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'
name='plone.introspector'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

setup(name=name,
      version=version,
      description="Introspection helpers for Zope and Plone.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3',
        ],
      keywords="zope zope2 plone web introspection introspector",
      author="Martin Lundwall, Lennart Regebro",
      author_email="martin@webworks.se",
      url='http://pypi.python.org/pypi/'+name,
      license="ZPL 2.1",
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zope.introspector',
                        'zope.introspectorui',
                        ],
      extras_require = dict(
        test=[]
      ),
      entry_points="""
      # Add entry points here
      """,
      )
