from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='safarisync',
      version=version,
      description="Tool for web scraping and syncing safari downloads library.",
      long_description="""\
A well documented example of screen scraping with lxml.  This example logins in to the safari book service, then synchronizes the files to the local system.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='lxml scraping',
      author='Douglas Mayle',
      url='http://douglas.mayle.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          "lxml",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      safarisync=safarisync.safarisync:main
      """,
      )
