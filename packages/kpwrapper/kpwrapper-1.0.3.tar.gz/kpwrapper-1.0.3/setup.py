#! /usr/bin/env python

from setuptools import setup, find_packages
import sys, os

version = '1.0.3'

setup(name='kpwrapper',
      version=version,
      description="Smart-M3 KP wrapper library",
      long_description=open("README.txt").read() + "\n" +
                             open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[ # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Intended Audience :: Developers',
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 2.6',
          'Topic :: Internet',
      ],
      keywords='Smart-M3 SIB KP',
      author='Eemeli Kantola',
      author_email='eemeli.kantola@iki.fi',
      url='http://asibsync.sourceforge.net',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
      include_package_data=True,
      zip_safe=True,
      dependency_links = [
          'http://public.futurice.com/~ekan/eggs',
      ],
      install_requires=[
          'smart-m3-pythonKP >=0.9.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
