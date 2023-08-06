from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='configurable',
      version=version,
      description="configurable - Class integration with config files",
      long_description="""\
Allows attributes of classes and/or instances to be set directly through config files""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ConfigParser configurable configuration Configfile config conffile',
      author='Krister Hedfors',
      author_email='krister@hedfors.se',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
