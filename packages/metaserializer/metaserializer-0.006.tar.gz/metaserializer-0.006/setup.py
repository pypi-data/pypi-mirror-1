#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <01-Mar-2010 14:54:03 PST by rich@noir.com>

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='metaserializer',
    version='0.006',
    author='K. Richard Pixley',
    author_email='rich@noir.com',
    description='A cover library for various other serializers.',
    license='MIT',
    keywords='serializer yaml pickle',
    url='http://packages.python.org/metaserializer',
    long_description=read('README'),
    setup_requires=[
    	'nose>=0.11.1',
    ],
    install_requires=[
    	"PyYAML>=3.09",
        "phpserialize",
    ],
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    py_packages=['metaserializer'],
    requires=[
        'json',
        'phpserialize',
        'pickle',
        'plistlib',
        'yaml',
    ],
    provides=[
        'metaserializer',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
