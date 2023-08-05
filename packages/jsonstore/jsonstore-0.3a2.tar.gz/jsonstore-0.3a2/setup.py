from setuptools import setup, find_packages
import sys, os

version = '0.3a2'

setup(name='jsonstore',
      version=version,
      description="A RESTful exposed database for arbitrary JSON objects.",
      long_description="""\
This package contains a WSGI app implementing a REST store accessible through a JSON syntax.""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://dealmeida.net/projects/jsonstore',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'Paste',
          'PasteScript',
          'PasteDeploy',
          'WebOb',
          'simplejson',
          'uuid',
      ],
      extras_require={
          'mysql': ['MySQL-python'],
          'sqlite': ['pysqlite>=2'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = jsonstore.store:make_app

      [jsonstore.backend]
      mysql = jsonstore.backends.mysql:EntryManager
      sqlite = jsonstore.backends.sqlite:EntryManager

      [paste.paster_create_template]
      jsonstore = jsonstore.template:JsonstoreTemplate
      """,
      )
      
