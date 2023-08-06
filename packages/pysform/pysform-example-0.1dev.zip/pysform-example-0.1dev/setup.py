from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pysform-example',
      version=version,
      description="an example application showing how to use pysform",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='randy',
      author_email='randy@rcs-comp.com',
      url='',
      license='',
      packages=['libs'] + find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pysapp>=dev',
          'pysform>=dev',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
