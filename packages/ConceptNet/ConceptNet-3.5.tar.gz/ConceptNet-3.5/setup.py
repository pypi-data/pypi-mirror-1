#!/usr/bin/env python

#Things we cannot easy_install: python-dev  can get from apt-get

from setuptools import setup, find_packages

#def add_prefix(prefix, x):
#    return [prefix+item for item in x]

packages = find_packages(exclude=['maint','legacy'])
#packages = ['csc']+add_prefix('csamoa.', packages)

try:
    import distutils
except ImportError:
    raise ImportError("You must manually install the package python-dev which contains distutils")

version_str = '3.5'
setup(  name='ConceptNet',
        version=version_str,
        description='A Python API to a Semantic Network Representation of the Open Mind Common Sense Project',
        author='Catherine Havasi, Robert Speer, Jason Alonso, and Kenneth Arnold',
        author_email='conceptnet@media.mit.edu',
        url='http://conceptnet.media.mit.edu/',
        download_url='http://conceptnet.media.mit.edu/dist/ConceptNet-%s.tar.gz' % version_str,
        packages=packages,
        package_dir = {'csamoa': ''},
        include_package_data=False,
        namespace_packages = ['csc'],
#        package_data={'csamoa': ['.LICENSE']},
        install_requires=['PyStemmer','django'],

        # Metadata
        license = "GPL v2",
        )
