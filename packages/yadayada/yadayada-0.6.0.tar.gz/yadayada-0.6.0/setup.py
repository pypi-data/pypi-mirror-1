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
    name='yadayada',
    version=__import__("yadayada", {}, {}, [""]).__version__,
    description='Common Django utilities',
    author='Ask Solem',
    author_email='askh@opera.com',
    packages=find_packages(exclude=['ez_setup']),
    #py_modules=['django.contrib.test.depth'],
    #url='http://pypi.python.org/pypi/download-portal/',
    install_requires=[
        'django>=1.0',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    long_description=codecs.open('README', "r", "utf-8").read(),
)
