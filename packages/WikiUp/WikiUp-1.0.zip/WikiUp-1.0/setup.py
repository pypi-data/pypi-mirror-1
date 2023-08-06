#!/usr/bin/env python
"""Distutils setup file"""
import sys
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

# Metadata
PROJECT = 'WikiUp'
VERSION = '1.0'
TAGLINE = 'Wiki page uploading command plugin for setuptools'

def get_description():
    # Get our long description from the documentation
    f = file('README.txt')
    lines = []
    for line in f:
        if not line.strip():
            break     # skip to first blank line
    for line in f:
        if line.startswith('.. contents::'):
            break     # read to table of contents
        lines.append(line)
    f.close()
    return ''.join(lines)

setup(
    name=PROJECT, version=VERSION, description=TAGLINE,
    url = "http://cheeseshop.python.org/pypi/" + PROJECT,
    long_description = file('README.txt').read(), #get_description(),
    author="Phillip J. Eby", author_email="peak@eby-sarna.com",
    license="PSF or ZPL", test_suite = 'wikiup', py_modules=['wikiup'],
    include_package_data = True, install_requires = ['mechanize'],
    entry_points = """
    [wikiup.plugins]
    OldMoin = wikiup:OldMoin
    [distutils.commands]
    wikiup = wikiup:wikiup""", classifiers=['Framework :: Setuptools Plugin'],
)
