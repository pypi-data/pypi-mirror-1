# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.sphinx.autoatschema
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

setup(name='collective.sphinx.autoatschema',
      version=version,
      description="Sphinx extension for archetypes schema",
      long_description=read('README.txt'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='zope archetypes sphinx documentation',
      author='Rok Garbas',
      author_email='rok@garbas.si',
      url='http://',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.sphinx'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['docutils', 'Sphinx', 'zc.recipe.egg'],
      )
