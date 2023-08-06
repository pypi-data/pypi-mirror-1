#!/usr/bin/env python
from setuptools import setup, find_packages

import ez_setup
ez_setup.use_setuptools()

setup(
    name='httprpclib',
    package_dir={'': 'src'},
    py_modules=['httprpclib'],
    version='0.1.1',

    author='Zachary Hirsch',
    author_email='zhirsch@umich.edu',
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
    description='A library that eases the use of RESTful web services',
    license='BSD',
    url='http://zhirsch.name/code/?p=httprpclib.git;a=summary',
)
