from setuptools import setup, find_packages
import sys, os

import commandline
version = '0.1.3'

setup(name='commandline',
      version=version,
      description="Exposes your APIs to the command line.",
      long_description=commandline.__doc__,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces",
          "Topic :: Utilities",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
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
