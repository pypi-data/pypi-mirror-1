#!/usr/bin/env python
#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages, Extension

long_description = """
Tools for manipulating data from lab experiments of internal gravity waves.

Implements a subclass of numpy.ndarray that includes a coordinate
system.  Slices give horizontal and vertical timeseries are stored in a HDF5
database. Includes matplotlib routines for plotting timeseries.  Also implements
a basic form of synthetic schlieren.
"""

setup(
    name='igwtools',
    version='0.3',
    packages = find_packages(),

    description = 'Tools for internal gravity waves experiments',
    author = 'James R. Munroe',
    author_email = 'jmunroe@ualberta.ca',
    license = "MIT",
    url = 'http://www.ualberta.ca/~jmunroe/igwtools',
    long_description = long_description,
    classifiers = ['License :: OSI Approved'],
#   ext_modules = [Extension('schlieren',['schlieren/schlieren.c'])],
    test_suite = "igwtools/test",
    entry_points = {
        'console_scripts':[
            'igwimport = igwtools.tools:import_entry',
            'igwschlieren = igwtools.schlieren:schlieren_entry',
            'igwextract = igwtools.tools:extract_entry',
            'xlook = igwtools.xplot:xlook',
            'xylook = igwtools.xplot:xylook',
            'xydiff = igwtools.xplot:xydiff',
            'jsi  = igwtools.imageproc:justshowit',
            'plot_traverse = igwtools.traverse:entry_plot_traverse',
            'showgrid  = igwtools.grids:showgrid',
            'igwgrid  = igwtools.grids:grid_entry',
        ]
    }
)

