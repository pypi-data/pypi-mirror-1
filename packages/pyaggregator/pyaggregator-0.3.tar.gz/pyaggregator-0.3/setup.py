from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='pyaggregator',
      version=version,
      description="Handles the tedious portions of aggregating web log posts",
#      long_description="""\
#Handles the tedious portions of aggregating web log posts
#""",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
      ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='blog rss atom feed',
      author='Neil Blakey-Milner',
      author_email='nbm@nxsy.org',
      #url='http://nxsy.org/code/pyaggregator/',
      license='MIT',
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
      
