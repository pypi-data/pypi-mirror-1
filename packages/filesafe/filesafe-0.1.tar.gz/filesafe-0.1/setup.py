from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='filesafe',
      version=version,
      description="An interface to safely perform file operations.",
      long_description="""\
Limit operations to a chroot directory, perform safe mapping and conversion of user input to filenames""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Douglas Mayle',
      author_email='douglas@mayle.org',
      url='http://dvdev.org',
      license='LGPL3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      test_suite='tests',
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
