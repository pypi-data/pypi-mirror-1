#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='roleplay',
    version='0.1',
    description='Python does Roles',
    author='Ask Solem',
    author_email='askh@opera.com',
    packages=find_packages(exclude=['ez_setup', 'examples']),
)

