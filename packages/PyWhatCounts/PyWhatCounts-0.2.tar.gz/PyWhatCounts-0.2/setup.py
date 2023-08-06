from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='PyWhatCounts',
      version=version,
      description="Python wrapper for WhatCounts HTTP API",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Jon Baldivieso',
      author_email='jonb@onenw.org',
      url='',
      license='',
      packages=find_packages('src'),
      package_dir={'':'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      dependency_links = [],
      )
