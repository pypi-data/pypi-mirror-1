from setuptools import setup, find_packages
import sys, os

import commandline
version = '0.1.2'

setup(name='commandline',
      version=version,
      description="Exposes your APIs to the command line.",
      long_description=commandline.__doc__,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='command line commandline script',
      author='David Laban',
      author_email='alsuren@gmail.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      test_suite = "commandline.test.suite",
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
