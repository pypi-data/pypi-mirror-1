#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='MinificationWebHelpers',
    version='0.1.0',
    description='Webhelpers CSS and JavaScript Minification Upgrade to WebHelpers',
    long_description = open('README.txt').read(),
    author='Pedro Algarvio',
    author_email='ufs@ufsoft.org',
    url='http://pastie.ufsoft.org',
    install_requires=["Pylons", "WebHelpers", "beaker", "cssutils"],
    packages=find_packages(),
    include_package_data=True,
)
