from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Meritocracy',
      version=version,
      description="Tool to access contribution statistics from a revision control system.",
      long_description="""\
Use this to generate contribution statistics and enable a meritocracy for your open source project.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Douglas Mayle',
      author_email='',
      url='http://douglas.mayle.org',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'SQLAlchemy',
          'mercurial>=1.1',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
