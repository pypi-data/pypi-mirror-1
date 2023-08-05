# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 by BlueDynamics Alliance, Klein & Partner KEG, Austria
#
# Zope Public License (ZPL)
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

from setuptools import setup, find_packages

name = "plone.recipe.dzhandle"
version = '1.0-beta2'

setup(
    name = name,
    version = version,
    author = "Jens W. Klein",
    author_email = "dev@bluedynamics.com",
    description = "ZC Buildout control for Debians zope instance handler 'dzhandle'",
          long_description="""\
This recipe creates and configures Zope zeoclients or zeoservers using Debians 
dzhandle approach. 

""",
    license = "ZPL 2.1",
    keywords = "zope buildout debian dzhandle",
    url='http://svn.plone.org/svn/collective/buildout/'+name,
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Zope2",
      "Operating System :: POSIX :: Linux",
      "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = ['zc.buildout', 'setuptools', 'zc.recipe.egg'],
    dependency_links = ['http://download.zope.org/distribution/'],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
