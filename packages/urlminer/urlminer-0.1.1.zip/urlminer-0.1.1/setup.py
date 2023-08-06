#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    print('setuptools not installed, using distutils.core')
    from distutils.core import setup


setup(name='urlminer',
      version='0.1.1',
      description='Provides a class for building RESTful applications and \
                   web services using a Resource Oriented Architecture',
      author='Stephen Day',
      author_email='stephen.h.day@gm**l.com',
      url='http://code.google.com/p/urlminer/',
      packages=['urlminer'],
      license = 'MIT',
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      long_description = """\
The aim of urlminer is to handle url traversal for your application. It doesn't
try (or want) to do much more, as other tools can easily be integrated, thanks
to WSGI. The only tools that *aren't* useful with urlminer are dispatchers, except
when they are used to direct requests to your application root.
"""
      )

