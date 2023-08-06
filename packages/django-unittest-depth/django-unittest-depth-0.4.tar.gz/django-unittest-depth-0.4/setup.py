#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='django-unittest-depth',
    version='0.4',
    description='Run django unittest recursively',
    author='Ask Solem',
    author_email='askh@opera.com',
    packages=find_packages(exclude=['ez_setup']),
    #py_modules=['django.contrib.test.depth'],
    url='http://pypi.python.org/pypi/django-unittest-depth/',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    long_description=codecs.open('README.txt', "r", "utf-8").read(),
)
