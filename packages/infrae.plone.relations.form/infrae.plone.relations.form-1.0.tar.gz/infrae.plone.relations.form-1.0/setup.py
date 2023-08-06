# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: setup.py 29203 2008-06-13 13:07:10Z sylvain $

from setuptools import setup, find_packages
import os.path

README_PATH = os.path.join('infrae', 'plone', 'relations', 'form')
long_description = """*************************************
Formlib widget for plone.app.relation
*************************************

.. contents::

""" + open(os.path.join(README_PATH, 'README.txt')).read() + \
      open(os.path.join('docs', 'HISTORY.txt')).read()
version = '1.0'

setup(name='infrae.plone.relations.form',
      version=version,
      description="Formlib widget to manage plone.app.relations relations in a plone site.",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='relationships plone widget formlib',
      author='Sylvain Viollon',
      author_email='sylvain@infrae.com',
      url='http://svn.infrae.com/PloneComponent/infrae.plone.relations.form/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['infrae',
                          'infrae.plone',
                          'infrae.plone.relations'],
      include_package_data=True,
      zip_safe=False,
      install_requires=["infrae.plone.relations.schema",
                        "setuptools"],
      )
