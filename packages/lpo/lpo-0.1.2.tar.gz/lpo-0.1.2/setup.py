# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# import sys, os

version = '0.1.2'

setup(name='lpo',
      version=version,
      description="Finite domain first order logic system",
      long_description="""\
Finite domain first order logic system""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='logic programming prolog',
      author='Enrique Perez Arnaud',
      author_email='enriquepablo@gmail.com',
      url='http://pypi.python.org/pypi/lpo',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'sqlalchemy >0.4,<0.5dev',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
