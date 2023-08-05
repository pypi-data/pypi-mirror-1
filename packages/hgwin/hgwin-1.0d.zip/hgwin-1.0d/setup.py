#!/usr/bin/env python2.5

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

#from distutils.core import setup

from hgwin import __version__ as version

setup(
    name='hgwin',
    version=version,
    description='hg serve manager for Windows using wxPython',
    author='Charles Mason, Andres Riofrio',
    author_email='cemasoniv@gmail.com, andresjriofrio@gmail.com',
    #url='',
    install_requires=["wxPython>=2.8.4.0"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data = True,
    entry_points = {'gui_scripts': ['hgwin = hgwin.hgwin:main']},
    classifiers=["Development Status :: 3 - Alpha"],
    )
