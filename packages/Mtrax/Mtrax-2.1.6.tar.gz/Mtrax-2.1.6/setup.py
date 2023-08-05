#!/usr/bin/env python

from setuptools import setup, Extension
from distutils.sysconfig import get_python_inc
from setuptools.dist import Distribution
import numpy
import numpy.numarray as nn
import os, glob
import sys

# include directories for hungarian
numpyincludedirs = numpy.get_include()
numarrayincludedirs = nn.get_numarray_include_dirs()
includedirs = numarrayincludedirs+[numpyincludedirs,]

# whether we have setuptools
if 'setuptools' in sys.modules:
    have_setuptools = True
else:
    have_setuptools = False

# read version number from version file
path = os.path.abspath( os.curdir )
mtrax_path = os.path.join( path, 'mtrax' )
ver_filename = os.path.join( mtrax_path, 'version.py' )
ver_file = open( ver_filename, "r" )
for line in ver_file: # parse through file version.py
    if line.find( '__version__' ) >= 0:
        line_sp = line.split() # split by whitespace
        version_str = line_sp[2] # third item
        this_version = version_str[1:-1] # strip quotes
ver_file.close()

# add all of the .xrc and .bmp files
mtrax_package_data = [ f[6:] for f in glob.glob('mtrax/*.xrc')]+\
                     [ f[6:] for f in glob.glob('mtrax/*.bmp')]
print 'mtrax_package_data: ',mtrax_package_data

setup( name="Mtrax",
       version=this_version,
       description="Multiple fly tracker",
       author="Caltech ethomics project",
       author_email="branson@caltech.edu",
       url="http://www.dickinson.caltech.edu/Research/Mtrax",
       packages=['mtrax'],
       entry_points = {'gui_scripts': ['mtrax=mtrax:main']},
       package_dir={'mtrax': 'mtrax',
                    'hungarian': 'hungarian',
                    'houghcircles': 'houghcircles'},
       package_data = {'mtrax':mtrax_package_data},
       #entry_points={'gui_scripts': ['mtrax=mtrax:main']},
       install_requires={'mtrax': ['setuptools>=0.6',
##                                   'wx>=2.6.3.2',
##                                   'numpy>=1.0',
##                                   'matplotlib>=0.87.5',
                                   'wxvideo'] # from Motmot
                         },
       ext_modules=[Extension('hungarian',['hungarian/hungarian.cpp',
                                           'hungarian/asp.cpp'],
                              include_dirs=includedirs),
                    Extension('houghcircles_C',
                              ['houghcircles/houghcircles_C.c'],
                              include_dirs=[numpyincludedirs,])
                    ]
       )
