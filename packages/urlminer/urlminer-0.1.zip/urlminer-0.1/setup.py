#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    print 'setuptools not installed, using distutils.core'
    print 'please ignore error message about "install_requires"'
    from distutils.core import setup


setup(name='urlminer',
      version='0.1',
      description='Provides a class for building RESTful applications and \
                   web services using a Resource Oriented Architecture',
      author='Stephen Day',
      author_email='stephen.h.day@gm**l.com',
      url='http://code.google.com/p/urlminer/',
      packages=['urlminer'],
      license = 'MIT',
      zip_safe = False,
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      )

