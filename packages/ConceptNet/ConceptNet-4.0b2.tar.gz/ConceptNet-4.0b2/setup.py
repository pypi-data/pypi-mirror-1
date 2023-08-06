#!/usr/bin/env python
from setuptools import setup, find_packages

packages = find_packages(exclude=['maint'])
version_str = '4.0b2'

setup(  name='ConceptNet',
        version=version_str,
        description='A Python API to a Semantic Network Representation of the Open Mind Common Sense Project',
        author='Catherine Havasi, Robert Speer, Jason Alonso, and Kenneth Arnold',
        author_email='conceptnet@media.mit.edu',
        url='http://conceptnet.media.mit.edu/',
        download_url='http://conceptnet.media.mit.edu/dist/ConceptNet-%s.tar.gz' % version_str,
        packages=packages,
        include_package_data=False,
        namespace_packages = ['csc'],
        install_requires=['PyStemmer', 'csc-utils'],

        # Metadata
        license = "GPL v2",
        )
