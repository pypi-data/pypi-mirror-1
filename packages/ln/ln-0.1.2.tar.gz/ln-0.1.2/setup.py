# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.1.2'

setup(name='ln',
      version=version,
      description="natural language proof of concept",
      long_description="""natural language proof of concept""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='natural language ai logic programming',
      author='Enrique Perez Arnaud',
      author_email='enriquepablo@gmail.com',
      url='http://pypi.python.org/pypi/nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'ln >=0.1',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
