from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='PyBus',
      version=version,
      description="PyBus is a message bus",
      long_description="""\
PyBus is a message bus that aims at providing message-level communication between items of the application (not distributed applications).
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='message bus',
      author='Bernardo Heynemann',
      author_email='heynemann@gmail.com',
      url='http://www.pybus.org',
      license='OSI',
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
