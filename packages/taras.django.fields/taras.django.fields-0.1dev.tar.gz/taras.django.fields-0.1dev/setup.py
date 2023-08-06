from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='taras.django.fields',
      version=version,
      description='''
      This package includes PickledField django field.
      ''',
      long_description="",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django field pickle',
      author='Taras Mankovski',
      author_email='tarasm@gmail.com',
      url='http://github.com/taras/taras.django.fields',
      license='BSD License',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['taras', 'taras.django'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
