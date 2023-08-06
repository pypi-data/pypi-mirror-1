from setuptools import setup, find_packages
import sys, os

version = '0.02'

setup(name='pyion',
      version=version,
      description="Core modules by Ion",
      long_description="""File handling, maths, randomization, miscellaneous""",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Programming Language :: Python :: 2.5',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
                   # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='file math random miscellaneous',
      author='David Gowers',
      author_email='00ai99@gmail.com',
      url='http://repo.or.cz/w/pyion.git',
      download_url='http://repo.or.cz/pyion.git',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'doc']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
