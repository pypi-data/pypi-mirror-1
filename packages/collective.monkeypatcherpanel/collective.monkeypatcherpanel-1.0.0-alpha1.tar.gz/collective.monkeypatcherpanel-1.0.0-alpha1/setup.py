# -*- coding: utf-8 -*-
# $Id: setup.py 84178 2009-04-13 18:02:35Z glenfant $
from setuptools import setup, find_packages
import os

version = '1.0.0-alpha1'

setup(name='collective.monkeypatcherpanel',
      version=version,
      description="A Zope 2 control panel that shows monkey patches applied by collective.monkeypatcher",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope monkey patch panel',
      author='Gilles Lenfant',
      author_email='gilles.lenfant@gmail.com',
      url='http://pypi.python.org/pypi/collective.monkeypatcherpanel',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.monkeypatcher'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
