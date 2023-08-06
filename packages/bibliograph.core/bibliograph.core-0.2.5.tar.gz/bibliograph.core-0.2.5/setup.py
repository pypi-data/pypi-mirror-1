# -*- coding: utf-8 -*-
"""
This module contains the core definitions of the bibliograph packages
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2.5'

long_description = (
    read('bibliograph', 'core', 'README.txt')
    + '\n' +
    'Change history\n'
    '--------------\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' 
    )

entry_points="""
# -*- Entry points: -*-
"""

setup(name='bibliograph.core',
      version=version,
      description="Core definitions of bibliograph packages",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='bibtex bibliography xml endnote ris bibutils',
      author='Tom Gross',
      author_email='itconsense@gmail.com',
      url='http://pypi.python.org/pypi/bibliograph.core',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bibliograph'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools'],
      tests_require=['zope.testing'],
      entry_points=entry_points,
      )
