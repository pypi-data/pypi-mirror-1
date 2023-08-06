from setuptools import setup, find_packages
import sys, os

import shiny
import shiny.test
version = '0.1'

setup(name='shiny',
      version=version,
      description="A collection of decorators to make your programs more shiny.",
      long_description=shiny.__doc__ ,# + shiny.test.doctests.__doc__,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Utilities",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='shiny decorators decorator library',
      author='David Laban',
      author_email='alsuren@gmail.com',
      url='http://alsuren.wordpress.com/tag/shiny/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      test_suite = "shiny.test.suite",
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
