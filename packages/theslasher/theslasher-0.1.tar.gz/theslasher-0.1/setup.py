from setuptools import setup, find_packages
import sys, os

version = "0.1"

setup(name='theslasher',
      version=version,
      description="removes trailing slashes",
      long_description="""
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org',
      license="",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = theslasher.factory:factory
      """,
      )
      
