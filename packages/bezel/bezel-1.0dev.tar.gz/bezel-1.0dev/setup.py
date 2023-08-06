#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='bezel',
    version=1.0,
    author='Peter Ward',
    author_email='peteraward@gmail.com',

    test_suite = 'tests.suite',

    packages = find_packages(exclude=['tests*']),

    install_requires=[
        'pygame>=1.7',
        'simplejson>=1.9.2',
        'pybonjour',
    ],
)

