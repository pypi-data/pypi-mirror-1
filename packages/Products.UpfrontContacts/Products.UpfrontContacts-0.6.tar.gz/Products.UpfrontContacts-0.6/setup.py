# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '0.6'

setup(name='Products.UpfrontContacts',
      version=version,
      description="Manage organisations, people and the relationships between them inside Plone and allow them to log in easily to your Plone site.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='contacts addressbook addresses',
      author='RC Compaan',
      author_email='roche at upfrontsystems dot co dot za',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
