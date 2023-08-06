from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='geohasher',
      version=version,
      description="Geohash without the iteration",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='geohash',
      author='Daniel Holth',
      author_email='dholth@fastmail.fm',
      url='http://dingoskidneys.com/',
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
