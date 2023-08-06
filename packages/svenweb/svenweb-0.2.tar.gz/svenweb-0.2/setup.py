from setuptools import setup, find_packages
import sys, os

version = "0.2"

long_description = open('README.txt').read()
changes = open('changes/changes.txt').read()
history = open('changes/history.txt').read()
future = open('changes/future.txt').read()

long_description = """%s

New in this version
-------------------

%s

What's next
-----------

%s

History
-------

%s
""" % (long_description, changes, future, history)

setup(name='svenweb',
      version=version,
      description="web frontend to versioncontrolled document repository for read-write-index-history operations",
      long_description=long_description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Ethan Jucovy and Jeff Hammel',
      author_email='ejucovy@gmail.com',
      url='',
      license="GPLv3 or later",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
         'WebOb',
         'Paste',
         'PasteScript',
         'Tempita',
         'simplejson',
         'sven>=0.7',
      ],

      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = svenweb.factory:factory
      [paste.filter_factory]
      content_type = svenweb.middleware.response.setter.content_type:filter_factory
      """,
      )
      
