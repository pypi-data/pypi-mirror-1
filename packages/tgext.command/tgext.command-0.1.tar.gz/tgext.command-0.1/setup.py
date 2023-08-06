from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='tgext.command',
      version=version,
      description="Cron-friendly TurboGears extension module",
      long_description="""\
Provides a TurboGears/Paster command base-class from which you can create cron-friendly command classes to be run from Paster.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='TurboGears,command line,pid,paster',
      author='Mike C. Fletcher',
      author_email='mcfletch@vrplumber.com',
      url='http://www.vrplumber.com',
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
