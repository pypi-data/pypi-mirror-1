#! /usr/bin/env python

from setuptools import setup, find_packages
import sys, os

version = '1.0.2'

setup(name='kpconsole',
      version=version,
      description="Smart-M3 KP console for interactive testing and debugging",
      long_description=open("README.txt").read() + "\n" +
                             open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[ # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.6',
          'Topic :: Internet',
      ],
      keywords='m3 sib kp console',
      author='Eemeli Kantola',
      author_email='eemeli.kantola@iki.fi',
      url='http://asibsync.sourceforge.net',
      license='BSD',
      py_modules=['kpconsole'],
      include_package_data=True,
      zip_safe=True,
      dependency_links = [
          
      ],
      install_requires=[
          'kpwrapper >=1.0.2',
          'ipython',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
