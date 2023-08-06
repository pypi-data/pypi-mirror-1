# -*- coding: utf-8 -*-
# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: setup.py 31075 2008-09-30 09:28:23Z sylvain $

from setuptools import setup, find_packages
import os

version = '1.2.3'

setup(name='Products.ProxyIndex',
      version=version,
      description="Zope 2 catalog index which fetch its data using a TAL expression.",
      long_description=open(os.path.join("Products", "ProxyIndex", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "ProxyIndex", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='zope catalog proxy index',
      author='Kapil Thangavel',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD and ZPL 2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
              'setuptools',
              ],
      )
