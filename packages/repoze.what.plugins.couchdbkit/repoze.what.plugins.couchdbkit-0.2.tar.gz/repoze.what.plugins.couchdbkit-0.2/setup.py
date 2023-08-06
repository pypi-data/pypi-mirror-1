from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='repoze.what.plugins.couchdbkit',
      version=version,
      description="repoze.what plugin for couchdbkit",
      long_description=open('README.txt').read(),
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='wsgi auth repoze what couchdb',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org/repoze.what.plugins.couchdbkit/index.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['repoze', 'repoze.what', 'repoze.what.plugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'couchdbkit',
          'repoze.what',
          'simplejson',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
