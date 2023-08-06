from setuptools import setup, find_packages
import sys, os

version = '0.1rc1'

setup(name='tg.ext.silverplate',
      version=version,
      description="TurboGears Registration and Administration module",
      long_description="""""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='TurboGears dbsprockets silverplate',
      author='Christopher Perkins',
      author_email='chris@percious.com',
      url='http://code.google.com/p/tgtools/',
      license='MIT',
      namespace_packages = ['tg.ext'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
