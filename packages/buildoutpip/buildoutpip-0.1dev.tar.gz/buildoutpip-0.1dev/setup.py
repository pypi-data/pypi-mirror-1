from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='buildoutpip',
      version=version,
      description="Buildout extension to install from pip requirements files",
      long_description=open('README.rst').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='buildout extension pip',
      author='Taras Mankovski',
      author_email='tarasm@gmail.com',
      url='http://github.com/taras/buildoutpip',
      license='BSD License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
	'zc.buildout.extension': ['ext = buildoutpip:extension'],
      } 
      )
