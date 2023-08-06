# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='quintagroup.portletmanager.footer',
      version=version,
      description="Portlet manager that is rendered in page footer",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portletmanager footer',
      author='Bohdan Koval',
      author_email='koval@quintagroup.com',
      url='http://svn.quintagroup.com/products/quintagroup.portletmanager.footer/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.portletmanager'],
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
