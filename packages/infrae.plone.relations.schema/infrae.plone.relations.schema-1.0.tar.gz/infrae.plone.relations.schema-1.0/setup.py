# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: setup.py 29099 2008-06-11 07:54:54Z sylvain $

from setuptools import setup, find_packages
import os.path

README_PATH = os.path.join('infrae', 'plone', 'relations', 'schema')
long_description = """*******************************************
Zope 3 schema field for plone.app.relations
*******************************************

.. contents::

""" + open(os.path.join(README_PATH, 'README.txt')).read() + \
      open(os.path.join(README_PATH, 'README.EXT.txt')).read() + \
      open(os.path.join('docs', 'HISTORY.txt')).read()
version = '1.0'

setup(name='infrae.plone.relations.schema',
      version=version,
      description="Zope 3 schema for plone.app.relations items.",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='relationships plone schema',
      author='Sylvain Viollon',
      author_email='sylvain@infrae.com',
      url='http://svn.infrae.com/PloneComponent/infrae.plone.relations.schema/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['infrae',
                          'infrae.plone',
                          'infrae.plone.relations'],
      include_package_data=True,
      zip_safe=False,
      install_requires=["plone.app.relations",
                        "setuptools"],
      )
