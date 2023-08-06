from setuptools import setup, find_packages
import os, sys

PACKAGE_NAME = "pouch"
PACKAGE_VERSION = "0.1.0"

SUMMARY = 'Python library for interfacing with couchdb'

DESCRIPTION = """This module provides an alternate object interface to couchdb than previously implemented by couchdb-python."""

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description=SUMMARY,
      long_description=DESCRIPTION,
      author='Mikeal Rogers',
      author_email='mikeal.rogers@gmail.com',
      url='http://code.google.com/p/pouch/',
      license='Python license',
      include_package_data = True,
      packages = find_packages(),
      platforms =['Any'],
      install_requires = ['simplejson', 'iso8601'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                  ],
     )
