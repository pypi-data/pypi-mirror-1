# Copyright 2009 Douglas Mayle

# This file is part of filesafe.

# filesafe is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# filesafe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with filesafe.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='filesafe',
      version=version,
      description="An interface to safely perform file operations.",
      long_description="""\
        Limit operations to a chroot directory, perform safe mapping and conversion of user input to filenames.
""",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Filesystems',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Douglas Mayle',
      author_email='douglas@mayle.org',
      url='http://dvdev.org',
      license='LGPLv3',
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
