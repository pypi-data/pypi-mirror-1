#!/usr/bin/env python

from distutils.core import setup

import httprpclib

setup(name='httprpclib',
      version=httprpclib.__version__,
      description='A library that eases the use of RESTful web services',
      long_description=httprpclib.__doc__,
      author=httprpclib.__author__,
      author_email=httprpclib.__author_email__,
      py_modules=['httprpclib'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      license='BSD',
)
