from setuptools import setup, find_packages
import sys, os

version = '0.1'
name ='inquant.recipe.download'

setup(name=name,
      user="seletz",
      version=version,
      description="A buildout recipe based on the gocept.download recipe which allows to clean out the destination.",
      long_description=file("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Buildout",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='buildout recipe',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='https://svn.inquant.de/inquant/develop/plone/recipes/'+name,
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['inquant', 'inquant.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "gocept.download", "zc.buildout", "setuptools"
      ],
      entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
      )
