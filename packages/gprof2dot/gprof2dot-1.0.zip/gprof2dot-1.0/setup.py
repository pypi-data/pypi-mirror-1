from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='gprof2dot',
      version=version,
      description="Generate a dot graph from the output of several profilers.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jose Fonseca',
      author_email='jose.r.fonseca@gmail com',
      url='http://jrfonseca.googlecode.com',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      gprof2dot=gprof2dot.gprof2dot:run
      """,
      )
