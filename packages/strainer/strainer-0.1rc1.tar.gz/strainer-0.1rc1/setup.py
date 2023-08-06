from setuptools import setup, find_packages
import sys, os

version = '0.1rc1'

setup(name='strainer',
      version=version,
      description="Tools to allow developers to cleanup web serialization objects (HTML, JSON, XHTML)",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='html xhtml json wsgi',
      author='Tom Lynn and Chris Perkins',
      author_email='chris@percious.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data={'strainer': ['dtds/*']},
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
