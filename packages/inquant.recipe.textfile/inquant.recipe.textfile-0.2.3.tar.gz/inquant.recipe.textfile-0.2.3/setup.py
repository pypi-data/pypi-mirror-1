from setuptools import setup, find_packages
import sys, os

version = '0.2.3'
name = 'inquant.recipe.textfile'

setup(name=name,
      version=version,
      description="ZC Buildout recipe for creating text files out of templates.",
      long_description=file("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Buildout",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='buildout recipe setup template',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='https://svn.inquant.de/inquant/develop/plone/recipes/'+name,
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[ 'inquant', 'inquant.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "zc.buildout", "setuptools"
      ],
      entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
      )
