#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for cuttlefish.
"""
from setuptools import setup, find_packages

PACKAGE_METADATA = dict(
    name="Cuttlefish",
    packages=find_packages(),
    include_package_data=True, # Requires setuptools_hg
    entry_points={
        'console_scripts': [
            'cuttlefish = cuttlefish:see_bottle_run',
        ],
    },
    zip_safe=False, # Needs a user-editable cuttlefish-config.plist
    install_requires=[
        'Bottle >= 0.6.4',
        'Mako >= 0.2.5',
    ],
    # PyPI metadata
    author='Kaelin Colclasure',
    author_email='kaelin@acm.org',
    platforms=['darwin', 'unix'],
    url='http://bitbucket.org/kaelin/cuttlefish/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        #'Framework :: Bottle',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Indexing',
    ],
)

def one_liner(line_a, line_b):
    line = line_a.strip()
    return (line, line_b.strip())[len(line) < 3]

def add_derived_metadata(desc):
    import cuttlefish
    desc['version'] = cuttlefish.__version__
    desc['license'] = cuttlefish.__license__
    desc['description'] = reduce(one_liner, cuttlefish.__doc__.split('\n'))
    with open('README.txt', 'r') as file:
        desc['long_description'] = file.read()

if __name__ == "__main__":
    add_derived_metadata(PACKAGE_METADATA)
    setup(**PACKAGE_METADATA)
