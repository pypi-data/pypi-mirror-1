from setuptools import setup, find_packages
import sys, os

version = "0.1"

setup(name='prettydate',
      version=version,
      description="pretty formatting of dates",
      long_description="""
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='The Open Planning Project',
      author_email='jhammel@openplans.org',
      url='http://topp.openplans.org',
      license="",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'python-dateutil'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = prettydate.web:factory
      """,
      )
      
