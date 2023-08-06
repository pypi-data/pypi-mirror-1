from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='oofill',
      version=version,
      description="OpenOffice blank filler",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='atReal',
      author_email='contact@atreal.net',
      url='https://svn.atreal.net/public/python/packages/oofill/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
