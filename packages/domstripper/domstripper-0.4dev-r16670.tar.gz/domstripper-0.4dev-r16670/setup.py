from setuptools import setup, find_packages
import sys, os

version = '0.4'

setup(name='domstripper',
      version=version,
      description="lxml.html based DOM manipulator",
      long_description="""\
Feed it a block of HTML and a list of CSS selectors and it will remove everything from the DOM tree except those elements you want to keep.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='html xml dom',
      author='Peter Bengtsson',
      author_email='peter@fry-it.com',
      url='http://www.peterbe.com/plog/domstripper',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      test_suite='test_domstripper',
      zip_safe=True,
      install_requires=[
          'lxml'
          
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
