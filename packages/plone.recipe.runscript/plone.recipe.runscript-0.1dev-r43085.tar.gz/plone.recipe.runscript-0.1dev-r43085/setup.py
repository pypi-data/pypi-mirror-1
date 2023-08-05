from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='plone.recipe.runscript',
      version=version,
      description="A buildout recipe to run a zope script",
      long_description=file("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='framework buildout recipe zope',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
	  [zc.buildout]
	  default = plone.recipe.runscript:Recipe
      """,
      )

# vim: set ts=4 sw=4 expandtab:
