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
    name='roleplay',
    version='0.11',
    description='Python does Roles',
    author='Ask Solem',
    author_email='askh@opera.com',
    packages=find_packages(exclude=['ez_setup', 'examples']),
    url='http://pypi.python.org/pypi/roleplay/',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    long_description=codecs.open('README.txt', "r", "utf-8").read(),
)
