# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='gp.fileupload',
      version=version,
      description="A WSGI middleware to get some stats on large files upload",
      long_description=open('README.txt').read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='wsgi middleware upload',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org',
      license='GPL',
      namespace_packages=['gp'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      sample = gp.fileupload.sampleapp:make_app

      [paste.filter_app_factory]
      main = gp.fileupload.middleware:make_app
      """,
      )
