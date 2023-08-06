from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='contentratings',
      version=version,
      description="A small Zope 3 package (which works best with Zope 2 and Five) that allows you to easily attach ratings to content.",
      long_description="",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Alec Mitchell',
      author_email='apm13@columbia.edu',
      url='http://plone.org/products/contentratings',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
